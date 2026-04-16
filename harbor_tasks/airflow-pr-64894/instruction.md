# Thread Safety Issue in CommsDecoder

## Problem

The `CommsDecoder` class has a concurrency bug. When multiple callers use a `CommsDecoder` instance concurrently, responses can be delivered to the wrong caller.

For example:
- Caller A sends a request for `key=foo`
- Caller B sends a request for `key=bar`
- Caller A receives the response for `key=bar` (wrong!)
- Caller B receives the response for `key=foo` (wrong!)

## Expected Behavior

Each call to `send()` must return only the response corresponding to that specific request, even when multiple threads call it concurrently. Responses must never be crossed between callers. The `asend()` async variant must follow the same thread-safety guarantee.

## Module API

The module `airflow.sdk.execution_time.comms` (located at `task-sdk/src/airflow/sdk/execution_time/comms.py`) exports these types. All must remain available and functional after the fix:

- `CommsDecoder` — the main decoder class, instantiated as `CommsDecoder(socket=<socket>, log=<structlog_logger>)`. Exposes `send(msg)` and `asend(msg)` methods, plus `_thread_lock` and `_async_lock` attributes.
- `_RequestFrame` — frame type for outgoing requests.
- `_ResponseFrame` — frame type for incoming responses. Supports two construction forms: positional `_ResponseFrame(id, body, error)` and keyword `_ResponseFrame(id=i, body=..., error=None)`. The `id` is an integer for correlating requests with responses, `body` is a dict such as `{"type": "VariableResult", "key": "...", "value": "..."}`, and `error` is `None` or an error value.
- `VariableResult` — message type constructed with keyword arguments `key`, `value`, and `type` (e.g., `VariableResult(key="foo", value="bar", type="VariableResult")`). Calling `send()` with a `VariableResult` returns a `VariableResult` whose `.key` and `.value` attributes contain the response data.

## Requirements

- The implementation must pass ruff linting (`ruff check`) and formatting (`ruff format --check`) on `task-sdk/src/airflow/sdk/execution_time/comms.py`.
- The repository's own tests in `task-sdk/tests/task_sdk/execution_time/test_comms.py` (specifically `TestCommsModels` and `TestCommsDecoder::test_huge_payload`) must continue to pass.
