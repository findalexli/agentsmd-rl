# Task: areal-rpc-error-response-key

## Bug Description

AReaL's RPC server and its scheduler clients are misaligned on the JSON key
used for error responses. The server's `/configure` endpoint returns error
messages under one key name, but both `local.py` and `slurm.py` schedulers
extract errors using a different key name — causing the real error message
to be silently replaced by the fallback `"Unknown error"`.

This makes RPC failures impossible to debug: for example, when an engine
`onload` fails, the traceback shows only "Unknown error" instead of the
actual traceback from the worker.

## Required Behavior

1. The `configure()` function in the RPC server must return JSON error
   responses with an `error` key (not `detail`). The response schema for
   each error path must include this `error` key with these specific messages:
   - `"Invalid JSON in request body"` — when `request.get_json()` returns None
   - `"Missing 'config' field in request"` — when the `config` key is absent
   - `"Missing 'rank' field in request"` — when the `rank` key is absent

2. Both scheduler clients (`local.py` and `slurm.py`) must extract error
   messages from server responses using `.get("error", "Unknown error")`.
   Each file must have at least two such error-extraction call sites
   (synchronous or async patterns), and they must successfully retrieve the
   actual error string from a `{"error": "..."}` response.

3. `proxy_gateway.py` uses `detail` per FastAPI/OpenAPI conventions and is
   out of scope for this task.