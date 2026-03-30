# Fix MCP tool-call latency for non-queued events

## Bug Description

When an MCP `call_tool()` is invoked for a non-queued event (`queue=False`), the current implementation routes the call through `gradio_client.Client.submit()`, which performs a full HTTP loopback: the MCP server makes an HTTP POST back to its own Gradio server, waits for the response through the queue/SSE mechanism, and blocks a thread waiting for the result. This adds approximately 4 seconds of overhead per call for functions that take only ~13ms to execute.

The call path is:
```
MCP request
  -> run_sync(Client._get_or_create_client)   # thread dispatch
  -> client.submit(api_name=endpoint)          # HTTP POST to own server
  -> Gradio queue processing
  -> run_sync(job.result)                      # thread blocking for HTTP response
```

For non-queued events, all of this overhead is unnecessary because `blocks.process_api()` can be called directly — it is the same internal function the HTTP route eventually reaches.

## What to Fix

In `gradio/mcp.py`, in the `call_tool()` method:

1. When `block_fn.queue` is `False`, bypass the HTTP loopback and call `blocks.process_api()` directly with the block function, inputs, and a fresh `SessionState`. Extract the output from `raw_output["data"]`.

2. When `block_fn.queue` is `True`, preserve the existing HTTP loopback path to maintain streaming updates, progress notifications, and queue-based features.

3. Import `SessionState` from `gradio.state_holder`.

4. Move the progress token and client creation logic inside the queued branch only.

## Affected Code

- `gradio/mcp.py` — the `call_tool()` method and related imports

## Acceptance Criteria

- Non-queued MCP tool calls use `blocks.process_api()` directly
- Queued MCP tool calls continue to use the HTTP loopback path
- `SessionState` is imported from `gradio.state_holder`
- The file remains syntactically valid Python
- Progress token handling is only done for queued events
