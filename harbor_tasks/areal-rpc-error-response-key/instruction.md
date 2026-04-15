# Task: areal-rpc-error-response-key

## Bug Description

AReaL's RPC server and its scheduler clients are misaligned on the JSON key
used for error responses. When a client makes a request to the server and an
error occurs, the server returns an error response, but the scheduler clients
extract the error message using a different key name — causing the actual
error details to be silently replaced by the fallback `"Unknown error"`.

For example, when an engine `onload` fails, the traceback shows only "Unknown
error" instead of the actual traceback from the worker. This makes RPC
failures impossible to debug.

## Required Behavior

1. The RPC server's `/configure` endpoint must return error responses using a
   JSON key that matches what the scheduler clients use for error extraction.
   The response schema for each error path must include this key with these
   specific messages:
   - `"Invalid JSON in request body"` — when JSON parsing fails
   - `"Missing 'config' field in request"` — when the config key is absent
   - `"Missing 'rank' field in request"` — when the rank key is absent

2. Both scheduler clients (`local.py` and `slurm.py`) must extract error
   messages from server responses using a `.get(...)` call with the fallback
   value `"Unknown error"`. Each file must have at least two such error
   extraction call sites (synchronous or async patterns), and they must
   successfully retrieve the actual error string from the server response.

   When the server returns an error response like `{"error": "Engine onload
   failed: CUDA OOM on device 0"}`, the scheduler must extract `"Engine onload
   failed: CUDA OOM on device 0"` — not `"Unknown error"`.

3. All 43 RPC server endpoints must use the same JSON key for error responses.
   Currently 42 endpoints use one key, but the `/configure` endpoint uses a
   different key, breaking round-trip consistency.

4. `proxy_gateway.py` is out of scope for this task.