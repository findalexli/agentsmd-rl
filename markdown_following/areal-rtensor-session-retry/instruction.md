# Fix: Connection resets during RTensor HTTP fetch with large payloads

## Problem

When using `HttpRTensorBackend` to fetch large tensor shards over HTTP (e.g., during
`compute_logp` for multimodal RL training), the connection frequently resets with
`Connection reset by peer` errors. This is especially common with payloads of several
megabytes. Additionally, any transient network hiccup during a fetch causes an immediate,
unrecoverable failure — even when the issue is temporary and a simple retry would succeed.

## Expected Behavior

1. **HTTP sessions must be configured for large tensor transfers.** The current default
   aiohttp session configuration uses a 300-second timeout (too short for large transfers)
   and a small read buffer. A properly configured session should use a larger timeout,
   a read buffer of at least 10 MB, and a `TCPConnector`.

2. **`_fetch_tensor` must retry on transient network errors** (e.g., `ClientError`,
   `TimeoutError`). After exhausting all retries, the raised error must include the
   number of attempts made.

3. **`fetch()` and `delete()` must create HTTP sessions properly.** Both methods currently
   create bare `aiohttp.ClientSession()` instances. They should create sessions that are
   configured for large tensor transfers (timeout, buffer, connector).

4. **`HttpRTensorBackend` must use a module-level logger** for structured log output,
   and this logger name must be registered in the color map.

## Code Style Requirements

- Python code must pass `ruff` linting (`ruff check`) and formatting (`ruff format
  --check`) as enforced by the project's pre-commit hooks. Follow existing code
  patterns in the module — do not introduce new conventions.

## Files to Modify

- `areal/infra/rpc/rtensor.py` — configure HTTP sessions properly for large transfers,
  add retry logic to the fetch method, add module-level logger
- `areal/utils/logging.py` — register the logger name in the color map