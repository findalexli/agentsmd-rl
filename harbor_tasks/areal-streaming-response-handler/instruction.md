# Task: Fix Streaming Response Handler

## Problem

The `/chat/completions` endpoint in the OpenAI proxy server raises a `ResponseValidationError` when handling streaming responses. The error occurs because FastAPI attempts to validate a streaming response as a non-streaming `ChatCompletion` object.

## Symptoms

1. When a request includes `{"stream": true}` in the body, the endpoint raises:
   ```
   ResponseValidationError: 1 validation error for ChatCompletion
   ```

2. The `stream` field from the request body leaks into the client call kwargs, interfering with explicit stream parameter control.

3. Streaming responses do not follow the OpenAI SSE format:
   - Each chunk should be: `data: {"id": "...", "content": "..."}\n\n`
   - Termination should be: `data: [DONE]\n\n`

## Target File

`/workspace/AReaL/areal/experimental/openai/proxy/proxy_rollout_server.py`

## Required Behavior

1. **Stream field isolation**: The request body's `stream` field must be removed from kwargs before the client call. The explicit `stream` parameter should control whether streaming actually occurs, independent of what the request body contained.

2. **SSE format compliance**: When streaming is enabled, the endpoint must yield Server-Sent Events matching this exact format:
   - Event prefix: `data: `
   - JSON payload containing `id` and `content` fields
   - Line ending: `\n\n`
   - Termination event: `data: [DONE]\n\n`

3. **Response validation bypass**: The endpoint must allow streaming responses without triggering FastAPI's `ResponseValidationError`. This requires either:
   - `response_model=None` in the route decorator, OR
   - Return type annotation of `StreamingResponse`

4. **Behavior under stream parameter combinations**:

   | Body stream | Param stream | Expected behavior |
   |-------------|--------------|-------------------|
   | `true`      | `false`      | Non-streaming (body value ignored) |
   | `true`      | `true`       | Streaming (body value ignored) |
   | `false`     | `false`      | Non-streaming (body value ignored) |
   | `false`     | `true`       | Streaming (body value ignored) |
   | omitted     | `false`      | Non-streaming |
   | omitted     | `true`       | Streaming |

## Verification

The fix is correct when:
- `ResponseValidationError` is no longer raised for streaming requests
- SSE clients receive properly formatted `data: ` events containing `id` and `content` fields
- Non-streaming requests continue to work as before
- The `stream` field from request body never reaches the underlying client call
