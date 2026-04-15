# Bug: /cancel endpoint leaks server-side generators

## Context

Gradio's streaming endpoints use server-side generators stored in `app.iterators`. When a streaming event finishes normally, the iterator is properly closed before being deleted from the dict.

However, when a user cancels a streaming event via the `/cancel` endpoint in `gradio/routes.py`, the iterator is deleted from `app.iterators` **without** being properly closed first. This means the generator's `finally` block never runs, and any cleanup logic (releasing resources, closing connections, etc.) is silently skipped.

## Reproduction

1. Create a Gradio Blocks app with a streaming generator function
2. Start a streaming event
3. Cancel the event via the `/cancel` endpoint
4. Observe that the generator's `finally` block (or cleanup code) never executes

## Expected behavior

When an event is cancelled via the `/cancel` endpoint:
- The generator's `finally` block must execute
- Any resources held by the generator must be properly released
- The cancellation should still succeed even if the cleanup code raises an exception
- After cancellation, the iterator should be removed from active tracking
