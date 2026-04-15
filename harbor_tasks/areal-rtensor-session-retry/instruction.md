# Fix: Connection resets during RTensor HTTP fetch with large payloads

## Problem

When using `HttpRTensorBackend` to fetch large tensor shards over HTTP (e.g., during
`compute_logp` for multimodal RL training), the connection frequently resets with
`Connection reset by peer` errors. This is especially common with payloads of several
megabytes. Additionally, any transient network hiccup during a fetch causes an immediate,
unrecoverable failure — even when the issue is temporary and a simple retry would succeed.

## Expected Behavior

1. **`HttpRTensorBackend` must create HTTP sessions using a dedicated session-creation
   method.** The method must be named one of: `_create_session`, `create_session`,
   `_make_session`, or `make_session`. It must be callable and must have an explicit
   return type annotation of `-> aiohttp.ClientSession`.

2. **The created session must be configured for large tensor transfers:**
   - The timeout must be set to `DEFAULT_REQUEST_TIMEOUT` from `areal.infra.utils.http`
     (this value is larger than the aiohttp default of 300 seconds).
   - The read buffer must be at least 10 MB.
   - The connector must be a `TCPConnector` obtained via `get_default_connector` from
     `areal.infra.utils.http`.

3. **`_fetch_tensor` must retry on transient network errors.** The method must accept:
   - `max_retries` (int): number of retry attempts before giving up
   - `retry_delay` (float): seconds to wait between retries
   After exhausting all retries, the raised `RuntimeError` must include the retry count
   (e.g., "... after 3 attempts").

4. **`fetch()` and `delete()` must use the session-creation method** (not a bare
   `aiohttp.ClientSession()` call) when creating their sessions.

5. **`HttpRTensorBackend` must use a module-level logger** named `"HttpRTensor"`
   obtained via `areal.utils.logging.getLogger`, and this logger name must be registered
   in the color map in `areal/utils/logging.py`.

## Files to Modify

- `areal/infra/rpc/rtensor.py` — add session-creation method with return type annotation,
  add retry logic to `_fetch_tensor` with `max_retries` and `retry_delay` parameters,
  update `fetch` and `delete` to use the new session-creation method, add module-level logger
- `areal/utils/logging.py` — add `"HttpRTensor"` to the color map