The `/chat/completions` endpoint in `areal/experimental/openai/proxy/proxy_rollout_server.py` raises a `ResponseValidationError` when a client sends `stream=true` in the request body.

There are two problems:

1. The `_call_client_create` helper does not strip the `stream` field from the request body kwargs. When a request includes `{"stream": true}`, the field leaks through to the underlying OpenAI client call via `**kwargs`, causing it to return an `AsyncGenerator` even when the endpoint did not explicitly request streaming via the `stream` parameter.

2. The `chat_completions` endpoint has no streaming branch. It always passes the return value of `_call_client_create` directly to FastAPI as a `ChatCompletion` response. When an `AsyncGenerator` is returned (because `stream` leaked through), FastAPI tries to validate it as a `ChatCompletion` dict and raises `ResponseValidationError`.

Fix both issues so that:
- The `stream` field from the request body is stripped in `_call_client_create` so only the explicit `stream` parameter controls streaming behavior.
- The `chat_completions` endpoint detects `stream=true` in the request and returns a proper `StreamingResponse` with Server-Sent Events in the OpenAI SSE format (`data: {json}\n\n` ... `data: [DONE]\n\n`).
