There is a JSON key mismatch between the RPC server and the scheduler clients in AReaL's infrastructure layer that causes real error messages to be silently lost.

The RPC server (`areal/infra/rpc/rpc_server.py`) returns error responses using the `"error"` key in 42 out of 45 places -- but 3 places in the `/configure` endpoint incorrectly use `"detail"` instead of `"error"`.

On the consumer side, both `areal/infra/scheduler/local.py` and `areal/infra/scheduler/slurm.py` read the error message using `.get("detail", "Unknown error")` in most error-handling branches. Since the server actually returns `{"error": "..."}`, the `.get("detail")` call always falls back to `"Unknown error"`, and the real error message from the worker is silently discarded.

This makes it impossible to debug RPC failures -- for example, when an engine `onload` fails, the traceback just shows "Unknown error" instead of the actual error message.

Fix the mismatch by:
1. Changing the 3 remaining `"detail"` keys in `rpc_server.py`'s `/configure` endpoint to `"error"` (aligning with the other 42 uses).
2. Changing all `.get("detail", "Unknown error")` calls in `local.py` and `slurm.py` to `.get("error", "Unknown error")`.

Note: `proxy_gateway.py` (FastAPI) intentionally uses `"detail"` following FastAPI/OpenAPI conventions and should NOT be changed.
