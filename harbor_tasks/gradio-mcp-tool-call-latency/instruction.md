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

## Symptom

MCP tool calls in `gradio/mcp.py` unconditionally use the HTTP loopback path via `gradio_client.Client`, even for non-queued events where direct internal function calls would suffice. This causes unnecessary latency overhead.

## Goal

Modify `gradio/mcp.py` to add a fast path for non-queued MCP tool calls that:
1. Bypasses the HTTP loopback mechanism for events where `queue=False`
2. Calls the Gradio blocks processing directly for such events
3. Preserves the existing HTTP loopback behavior for queued events (queue=True)
4. Maintains progress token handling only where needed for queue-based features
5. Keeps the file syntactically valid and importable

The fix should eliminate the ~4 second latency overhead for non-queued MCP tool calls while maintaining backward compatibility for streaming/queued events.
