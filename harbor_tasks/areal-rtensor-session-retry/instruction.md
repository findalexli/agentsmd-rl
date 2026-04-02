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
   connector settings already established in `areal/infra/utils/http.py`
2. Tensor fetches should retry on transient network errors (connection resets, timeouts)
   before giving up, with configurable retry count and delay
3. Proper logging should be added so transient failures are visible in logs

## Files to Investigate

- `areal/infra/rpc/rtensor.py` — `HttpRTensorBackend._fetch_tensor`, `fetch`, `delete`
- `areal/infra/utils/http.py` — existing HTTP session configuration utilities
- `areal/utils/logging.py` — logger color registration
