# Fix Race Condition in Conversation Creation

## Problem

There's a race condition in the OpenHands frontend where clicking "New Conversation" can accidentally create a V0 (legacy) conversation instead of a V1 conversation. This happens when the user clicks before the settings query has resolved.

## Symptoms

- If a user clicks "New Conversation" quickly after page load (before settings are loaded), the conversation is created using the legacy V0 API instead of V1
- This causes inconsistent behavior and potentially missing features
- The bug is timing-dependent and hard to reproduce consistently

## Root Cause

The `useCreateConversation` hook checks `settings?.v1_enabled` to decide between V1 and V0 APIs. If settings haven't loaded yet, `settings` is `undefined`, causing `!!undefined?.v1_enabled` to evaluate to `false` — silently routing through the legacy V0 code path.

Additionally, `DEFAULT_SETTINGS.v1_enabled` defaults to `false` on the frontend while the backend defaults to `true`, creating a mismatch.

## Files to Modify

1. **`frontend/src/services/settings.ts`** - Change `DEFAULT_SETTINGS.v1_enabled` from `false` to `true`
2. **`frontend/src/hooks/mutation/use-create-conversation.ts`** - Wait for settings to load before deciding V0 vs V1, use proper fallback
3. **`frontend/src/hooks/query/use-settings.ts`** - Export `getSettingsQueryFn` for use in the mutation hook

## Requirements

The fix should:
- Align frontend default with backend default (`v1_enabled: true`)
- Wait for settings to be available before deciding which API to use
- Fall back to `DEFAULT_SETTINGS` if settings fetch fails (e.g., 404 for new users)
- Still respect explicit `v1_enabled: false` for organizations that have V1 disabled
- Use the organization ID in the query key for proper caching

## Hints

- Look at how TanStack Query's `ensureQueryData` works for waiting on queries
- The fix should use a try/catch to handle settings fetch failures
- You'll need to import `useSelectedOrganizationId` to get the organization context
- Make sure to export the query function from `use-settings.ts` so it can be used in the mutation
