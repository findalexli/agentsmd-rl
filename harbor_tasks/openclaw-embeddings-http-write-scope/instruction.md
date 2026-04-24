# Bug: /v1/embeddings endpoint missing operator write scope enforcement

## Summary

The OpenAI-compatible `/v1/embeddings` gateway endpoint does not enforce any operator scope check before processing requests. All other write-oriented OpenAI-compatible HTTP endpoints (e.g., `/v1/chat/completions`) require the caller to hold `operator.write` privilege, but the embeddings endpoint was wired up without this gate.

This means an operator with only `operator.read` scope — or even an empty scope set — can call `/v1/embeddings` and generate embeddings, bypassing the intended authorization model.

## Reproduction

1. Start the gateway with token auth enabled.
2. Send a POST to `/v1/embeddings` with a valid bearer token but with the `x-openclaw-scopes` header set to `operator.read` (no write scope).
3. Observe: the request succeeds with 200 and returns embeddings.
4. Expected: the request should be rejected with 403, like the other write endpoints.

## Required Fix

The `handleOpenAiEmbeddingsHttpRequest` function in `src/gateway/embeddings-http.ts` calls `handleGatewayPostJsonEndpoint` to handle auth and request processing. This call must pass `requiredOperatorMethod: "chat.send"` in its options object to enforce the write scope check. The value `"chat.send"` is the canonical operator method that requires `operator.write` scope, as defined in `src/gateway/method-scopes.ts` and used by other write-gated endpoints like `/v1/chat/completions`.

## Verification

After the fix, the `handleGatewayPostJsonEndpoint` call in `handleOpenAiEmbeddingsHttpRequest` must include `requiredOperatorMethod: "chat.send"` alongside the existing `pathname: "/v1/embeddings"` option.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `eslint (JS/TS linter)`
