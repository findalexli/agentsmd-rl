# Fix Race Condition in Conversation Creation

## Problem

There's a race condition in the OpenHands frontend where clicking "New Conversation" can accidentally create a V0 (legacy) conversation instead of a V1 conversation. This happens when the user clicks before the settings query has resolved.

## Symptoms

- If a user clicks "New Conversation" quickly after page load (before settings are loaded), the conversation is created using the legacy V0 API instead of V1
- This causes inconsistent behavior and potentially missing features
- The bug is timing-dependent and hard to reproduce consistently

## Observed Behavior

The `useCreateConversation` hook checks `settings?.v1_enabled` to decide between V1 and V0 APIs. If settings haven't loaded yet, `settings` is `undefined`, causing `!!undefined?.v1_enabled` to evaluate to `false` — silently routing through the legacy V0 code path.

The frontend defaults `v1_enabled` to `false` in its settings, but the backend defaults it to `true`, creating a mismatch between frontend and backend behavior.

## Required Changes

The following specific changes are needed to fix this issue:

1. **`frontend/src/services/settings.ts`** — The `DEFAULT_SETTINGS` object contains a `v1_enabled` property that must be `true` (not `false`) to align with the backend default

2. **`frontend/src/hooks/query/use-settings.ts`** — The `getSettingsQueryFn` function must be exported so it can be used by other hooks

3. **`frontend/src/hooks/mutation/use-create-conversation.ts`** — This hook must:
   - Wait for settings to be available before deciding which API to use
   - Use a query-key pattern that includes the organization ID for proper cache isolation
   - Fall back to `DEFAULT_SETTINGS` when settings cannot be fetched (e.g., 404 for new users who don't have settings yet)
   - Respect explicit `v1_enabled: false` for organizations that have V1 disabled

## Technical Notes

- The backend defaults `v1_enabled` to `true`, so the frontend should match this default
- The TanStack Query `ensureQueryData` helper can be used to wait for a query to complete before proceeding
- When settings fetch fails, a sensible fallback is to use the default settings object
- The organization ID should be included in the query key to ensure proper cache per-organization
- The existing `!!settings?.v1_enabled` pattern silently fails when settings is `undefined` — a different approach is needed

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`
