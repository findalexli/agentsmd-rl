# Fix Next.js replaceState Bug in Auth Store

There's a bug in Next.js (https://github.com/vercel/next.js/issues/91819) where `history.replaceState` is called twice in certain scenarios. This causes issues with the session ID handling in Sanity's auth store.

## The Problem

In the auth callback URL handling, the session ID is extracted from the URL hash and removed using `history.replaceState()`. However, due to the Next.js bug, `replaceState` can be called twice, which can leave the session ID (`sid`) parameter in the URL when it should have been removed. This leads to errors like "Session with sid (...) not found" when the auth callback is processed.

## Your Task

Implement a workaround for this Next.js bug that ensures the session ID is properly cleared from the URL even when `replaceState` is called twice.

The implementation must satisfy these requirements:

1. In `packages/sanity/src/core/store/_legacy/authStore/sessionId.ts`, export a function named `clearSessionId` with the exact signature:
   ```typescript
   export function clearSessionId(): void
   ```
   This function should be a simple wrapper that calls the existing `consumeSessionId()` function.

2. In `packages/sanity/src/core/store/_legacy/authStore/createAuthStore.ts`, import `clearSessionId` from `./sessionId` alongside the existing `getSessionId` import.

3. In the `handleCallbackUrl` function within `createAuthStore.ts`, after calling `getSessionId()` to obtain the session ID, call `clearSessionId()` to ensure the session ID is cleared again as a workaround for the double `replaceState` bug.

4. Include a comment referencing `https://github.com/vercel/next.js/issues/91819` near the workaround code to document why this extra clearing is necessary.

## Relevant Files

- `packages/sanity/src/core/store/_legacy/authStore/sessionId.ts` - Contains session ID extraction logic including `consumeSessionId`
- `packages/sanity/src/core/store/_legacy/authStore/createAuthStore.ts` - Contains the auth store and callback URL handling

## Notes

- The repo uses pnpm (v10+) and Node.js v24+
- Run `pnpm install` before building
- Build with `pnpm build` before testing
- Type checking, linting, and all existing tests must still pass
