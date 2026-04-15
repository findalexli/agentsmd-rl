# Bug: OpenResponses HTTP ingress grants owner-level privileges to external API callers

## Summary

The OpenResponses HTTP handler (`src/gateway/openresponses-http.ts`) processes incoming `/v1/responses` requests from external API callers. These HTTP callers are authenticated operator clients, but they should **not** be treated as "owners" — owner status unlocks access to owner-only tools that external callers should never reach.

Currently, when the handler dispatches agent commands for both streaming and non-streaming response paths, it unconditionally grants owner-level access to every HTTP caller. This means any authenticated HTTP client can request elevated scopes (e.g., `operator.admin`, `operator.write`) and the system will honor them as if the caller were the owner.

## Reproduction

1. Send a POST to `/v1/responses` with any valid authentication.
2. Include elevated scope headers (e.g., `x-openclaw-scopes: operator.admin, operator.write`).
3. Observe that the agent command execution treats the caller as an owner, making owner-only tools available.

## Expected behavior

HTTP ingress callers should always be treated as non-owners. Requested HTTP scopes should not be able to upgrade the caller's owner status. Both the streaming and non-streaming execution paths must pass an explicit non-owner indicator (not a hardcoded `true`) to the underlying agent command dispatcher.

## Implementation requirements

The fix must satisfy all of the following constraints:

1. **Non-owner indicator must flow from parameters**: The parameter controlling owner status must be received from callers and passed through to the agent command dispatcher — it must not be hardcoded as a literal `true` inside the helper function.

2. **Strict boolean typing**: The owner-status parameter must be explicitly typed as `boolean` in the function signature or type definition (no implicit `any`, no union including `any`).

3. **No sentinel defaults**: The owner-status parameter must not use silent sentinel defaults like `?? true` or `?? false`.

4. **Both call sites must pass non-owner values**: Both streaming and non-streaming paths in the handler must pass a non-owner value (something other than literal `true`).

5. **Configuration preserved**: The `allowModelOverride: true` configuration in the file must remain intact.

6. **No suppressions**: The file must not contain `@ts-nocheck`, `eslint-disable`, or `oxlint-ignore` suppressions.

7. **No stub code**: The file must contain at least 400 lines and the helper function must have a substantial body (not be a stub or empty).