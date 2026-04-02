# Bug: /cancel endpoint leaks server-side generators

## Context

Gradio's streaming endpoints use server-side generators (wrapped as `SyncToAsyncIterator`) stored in `app.iterators`. When a streaming event finishes normally, the queue's `reset_iterators()` method in `gradio/queueing.py` properly closes the iterator via `safe_aclose_iterator()` before deleting it from the dict.

However, when a user cancels a streaming event via the `/cancel` endpoint in `gradio/routes.py`, the iterator is deleted from `app.iterators` **without** being properly closed first. This means the generator's `finally` block never runs, and any cleanup logic (releasing resources, closing connections, etc.) is silently skipped.

## Reproduction

1. Create a Gradio Blocks app with a streaming generator function
2. Start a streaming event
3. Cancel the event via the `/cancel` endpoint
4. Observe that the generator's `finally` block (or cleanup code) never executes

## Where to look

- `gradio/routes.py` — the `cancel_event` handler (search for `async def cancel_event`)
- `gradio/queueing.py` — `reset_iterators()` already handles this correctly; the cancel endpoint should follow the same pattern
- `gradio/utils.py` — `safe_aclose_iterator()` is the utility used to properly close iterators

## Expected behavior

When an event is cancelled, the `/cancel` endpoint should properly close the iterator (calling `safe_aclose_iterator()`) before removing it, just like `reset_iterators()` does.
