# Performance Bug: O(n) front-removal in SSE pending message queues

## Context

The `gradio_client` Python library uses Server-Sent Events (SSE) for streaming communication with Gradio servers. During SSE streaming, incoming messages are buffered into per-event queues (`pending_messages_per_event`) and consumed front-to-back by the streaming functions.

## Bug

In `client/python/gradio_client/client.py` and `client/python/gradio_client/utils.py`, the pending message queues are implemented as plain Python `list` objects. Messages are appended to the back and removed from the front using `.pop(0)`.

The problem: `list.pop(0)` is **O(n)** because Python must shift every remaining element forward. For long-running streaming sessions with many pending messages, this causes quadratic-time degradation. The queue operations should be **O(1)** for both append and front-removal.

## Files to investigate

- `client/python/gradio_client/client.py` — look at `pending_messages_per_event` initialization in `Client.__init__`, `stream_messages`, and `_predict`
- `client/python/gradio_client/utils.py` — look at `stream_sse_v1plus` and `get_pred_from_sse_v1plus`, specifically the `.pop(0)` call and the type annotations

## Expected behavior

Front-removal from the pending message queues should be O(1), not O(n). The fix should use the appropriate Python standard library data structure for efficient FIFO operations, updating all initialization sites, type annotations, and consumption sites consistently.
