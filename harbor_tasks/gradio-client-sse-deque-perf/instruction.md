# Performance Bug: Quadratic Degradation in SSE Message Queues

## Context

The `gradio_client` Python library uses Server-Sent Events (SSE) for streaming communication with Gradio servers. During SSE streaming, incoming messages are buffered into per-event queues and consumed front-to-back.

## Bug

In `client/python/gradio_client/client.py` and `client/python/gradio_client/utils.py`, the pending message queues are implemented as plain Python `list` objects. Messages are appended to the back and removed from the front using standard list operations.

The problem: removing elements from the front of a list is **O(n)** because Python must shift every remaining element forward. For long-running streaming sessions with many pending messages, this causes quadratic-time degradation.

## Symptom

When the SSE streaming code removes messages from the front of pending message queues, it uses an O(n) operation. For high-volume streaming, this causes performance degradation proportional to the square of the message count.

## Expected behavior

Queue operations (appending to the back and removing from the front) should be **O(1)** for predictable streaming performance. Update the data structures and all related code (initializations, type annotations, and consumption sites) consistently.

## Files to investigate

- `client/python/gradio_client/client.py`
- `client/python/gradio_client/utils.py`

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check`
