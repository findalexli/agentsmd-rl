# Fix: Connection resets during RTensor HTTP fetch with large payloads

## Problem

When using `HttpRTensorBackend` to fetch large tensor shards over HTTP (e.g., during
`compute_logp` for multimodal RL training), the connection frequently resets with
`Connection reset by peer` errors. This is especially common with payloads of several
megabytes. Additionally, any transient network hiccup during a fetch causes an immediate,
unrecoverable failure — even when the issue is temporary and a simple retry would succeed.

## Root Cause

`HttpRTensorBackend` creates a bare `aiohttp.ClientSession()` with no explicit timeout,
buffer size, or connector configuration. The default aiohttp session uses a small read
buffer and generic connection settings that are not suited for large tensor transfers.
The existing HTTP utility module (`areal/infra/utils/http.py`) already defines
properly-configured session defaults (including a generous timeout, a large read buffer,
and a `TCPConnector`) — but `HttpRTensorBackend` does not use them.

Furthermore, `_fetch_tensor` has no retry logic at all: a single transient error
(`TimeoutError`, `ClientError`) immediately propagates up and aborts the entire batch
fetch.

## Expected Behavior

1. `HttpRTensorBackend` should create HTTP sessions with the same timeout, buffer, and
   connector settings already established in `areal/infra.utils.http`. The session must:
   - Use `DEFAULT_REQUEST_TIMEOUT` from `areal.infra.utils.http` as the timeout total
   - Use a read buffer of at least 10 MB
   - Use the default `TCPConnector` from `areal.infra.utils.http`

2. Tensor fetches should retry on transient network errors (connection resets, timeouts,
   client errors) before giving up. The `_fetch_tensor` method must accept:
   - `max_retries` (int): number of retry attempts
   - `retry_delay` (float): seconds to wait between retries
   After exhausting all retries, the error message must include the retry count.

3. The `HttpRTensorBackend` backend must use a module-level logger named `"HttpRTensor"`
   obtained via `areal.utils.logging.getLogger`, and this logger name must be registered
   in the color map in `areal/utils/logging.py`.

4. The session-creation method must have an explicit return type annotation `-> aiohttp.ClientSession`.

## Files to Modify

- `areal/infra/rpc/rtensor.py` — add session-creation method, retry logic to `_fetch_tensor`,
  update `fetch` and `delete` to use the new session method
- `areal/utils/logging.py` — register the `"HttpRTensor"` logger name in the color map