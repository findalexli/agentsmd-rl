# Bug: /v1/embeddings endpoint missing operator write scope enforcement

## Summary

The OpenAI-compatible `/v1/embeddings` gateway endpoint does not enforce any operator scope check before processing requests. All other write-oriented OpenAI-compatible HTTP endpoints (e.g., `/v1/chat/completions`) require the caller to hold `operator.write` privilege, but the embeddings endpoint was wired up without this gate.

This means an operator with only `operator.read` scope — or even an empty scope set — can call `/v1/embeddings` and generate embeddings, bypassing the intended authorization model.

## Reproduction

1. Start the gateway with token auth enabled.
2. Send a POST to `/v1/embeddings` with a valid bearer token but with the `x-openclaw-scopes` header set to `operator.read` (no write scope).
3. Observe: the request succeeds with 200 and returns embeddings.
4. Expected: the request should be rejected with 403, like the other write endpoints.

## Relevant code

- `src/gateway/embeddings-http.ts` — the `handleOpenAiEmbeddingsHttpRequest` function calls `handleGatewayPostJsonEndpoint` to handle auth, body parsing, and scope checks.
- `src/gateway/http-endpoint-helpers.ts` — the shared helper already supports scope enforcement via an option that other endpoints pass but embeddings does not.
- `src/gateway/method-scopes.ts` — defines which methods require which operator scopes.

## Scope

The fix should align the embeddings endpoint's authorization with the other OpenAI-compatible write endpoints so that callers without write scope are properly rejected. The existing tests in `src/gateway/embeddings-http.test.ts` should be updated to declare write scope for successful requests and to add coverage for rejected scope scenarios.
