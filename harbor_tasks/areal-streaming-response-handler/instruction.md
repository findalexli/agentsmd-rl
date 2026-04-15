# Task: Fix Streaming Response Handler

## Problem

The `/chat/completions` endpoint in `areal/experimental/openai/proxy/proxy_rollout_server.py` raises a `ResponseValidationError` when a client sends `stream=true` in the request body.

## Symptoms

1. When a request includes `{"stream": true}` in the body, the OpenAI client returns an `AsyncGenerator` instead of a `ChatCompletion` dict, causing FastAPI validation to fail with `ResponseValidationError`.

2. Even when the explicit `stream` parameter is used, the response format is incorrect for SSE streaming clients.

## Required Behaviors

The implementation must satisfy all of the following:

1. **Stream field isolation**: The `stream` field from the request body must not reach the underlying OpenAI client call via `**kwargs`. Only the explicit `stream` parameter passed to the client should control streaming behavior.

2. **SSE format compliance**: When streaming is enabled, the endpoint must return Server-Sent Events in the OpenAI SSE format:
   - Each chunk: `data: {json}\n\n` (JSON contains `id` and `content` fields)
   - Termination: `data: [DONE]\n\n`

3. **Streaming response support**: The endpoint must be capable of returning a streaming response without FastAPI attempting to validate it as a non-streaming `ChatCompletion` response.

4. **Behavior under stream parameter combinations**:

   | Body stream | Param stream | Expected behavior |
   |-------------|--------------|-------------------|
   | `true`      | `false`      | Strip body stream, non-streaming |
   | `true`      | `true`       | Strip body stream, streaming |
   | `false`     | `false`      | Strip body stream, non-streaming |
   | `false`     | `true`       | Strip body stream, streaming |
   | omitted     | `false`      | No stream in kwargs, non-streaming |
   | omitted     | `true`       | Add stream=True to kwargs, streaming |

## Verification

The fix is correct when:
- `ResponseValidationError` is no longer raised for streaming requests
- SSE clients receive properly formatted `data: ` events with `content` fields
- Non-streaming requests continue to work as before