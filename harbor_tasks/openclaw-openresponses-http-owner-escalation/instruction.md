# Bug: OpenResponses HTTP ingress grants owner-level privileges to external API callers

## Summary

The OpenResponses HTTP handler (`src/gateway/openresponses-http.ts`) processes incoming `/v1/responses` requests from external API callers. These HTTP callers are authenticated operator clients, but they should **not** be treated as "owners" — owner status unlocks access to owner-only tools that external callers should never reach.

Currently, when the handler dispatches agent commands for both streaming and non-streaming response paths, it unconditionally grants owner-level access to every HTTP caller. This means any authenticated HTTP client can request elevated scopes (e.g., `operator.admin`, `operator.write`) and the system will honor them as if the caller were the owner.

## Reproduction

1. Send a POST to `/v1/responses` with any valid authentication.
2. Include elevated scope headers (e.g., `x-openclaw-scopes: operator.admin, operator.write`).
3. Observe that the agent command execution treats the caller as an owner, making owner-only tools available.

## Expected behavior

HTTP ingress callers should always be treated as non-owners. Requested HTTP scopes should not be able to upgrade the caller's owner status. This applies to both the streaming and non-streaming execution paths in `handleOpenResponsesHttpRequest`.

## Relevant files

- `src/gateway/openresponses-http.ts` — the `runResponsesAgentCommand` helper and `handleOpenResponsesHttpRequest` function
