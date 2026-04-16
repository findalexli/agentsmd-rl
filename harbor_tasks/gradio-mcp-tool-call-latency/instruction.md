# Fix MCP tool-call latency for non-queued events

## Bug Description

When an MCP `call_tool()` is invoked, the call currently goes through `gradio_client.Client.submit()`, which performs a full HTTP loopback: the MCP server makes an HTTP POST back to its own Gradio server, waits for the response through the queue/SSE mechanism, and blocks a thread waiting for the result. This adds approximately 4 seconds of overhead per call for functions that take only ~13ms to execute.

The call path is:
```
MCP request
  -> run_sync(Client._get_or_create_client)   # thread dispatch
  -> client.submit(api_name=endpoint)          # HTTP POST to own server
  -> Gradio queue processing
  -> run_sync(job.result)                      # thread blocking for HTTP response
```

## Symptom

MCP tool calls in `gradio/mcp.py` unconditionally use the HTTP loopback path via `gradio_client.Client`, even for events where faster internal processing is available. This causes unnecessary latency overhead.

## Goal

Reduce the latency overhead for MCP tool calls. The implementation must:

1. Be syntactically valid Python, pass ruff linting, and be importable as `from gradio import mcp`
2. For the code path taken when `queue=False`:
   - Import `SessionState` from `gradio.state_holder` into the `gradio.mcp` namespace
   - Use the `blocks.process_api()` method of the Gradio blocks instance
   - Extract output from the `["data"]` key of the `process_api` result dictionary
3. For the code path taken when `queue=True`:
   - Continue to use `client.submit()` (HTTP loopback) so that streaming updates and progress notifications continue to work
4. Ensure the queued path does NOT call `blocks.process_api()`

The fix should maintain backward compatibility for streaming/queued events while eliminating the ~4 second latency overhead for non-queued MCP tool calls.