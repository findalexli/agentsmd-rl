# OpenHands: Fix V0 Conversation Race Condition

## Bug Description

Clicking "New Conversation" can accidentally create a V0 (legacy) conversation instead of V1 due to a race condition in settings loading.

### Root Cause

The `useCreateConversation` hook checks `settings?.v1_enabled` to decide between V1 and V0 APIs. If the user clicks "New Conversation" before the settings query resolves, `settings` is `undefined`, causing `!!undefined?.v1_enabled` to evaluate to `false` — silently routing through the legacy V0 code path.

This is compounded by `DEFAULT_SETTINGS.v1_enabled` being `false` on the frontend while the backend defaults to `true` everywhere.

### Files Involved

1. **frontend/src/services/settings.ts** — DEFAULT_SETTINGS object
2. **frontend/src/hooks/mutation/use-create-conversation.ts** — useCreateConversation hook logic
3. **frontend/__tests__/hooks/mutation/use-create-conversation-race-condition.test.tsx** — Race condition tests

## Expected Behavior

- Frontend should default to V1 conversation creation when settings are undefined or not yet loaded
- When settings explicitly set `v1_enabled: false`, respect that and use V0
- The fallback behavior should match the backend default

## Test Notes

The test suite in `frontend/__tests__/hooks/mutation/` verifies:
- V1 creation when settings undefined (race condition case)
- V1 creation when settings not yet loaded
- Fallback to V1 when settings fetch fails
- V0 creation only when explicitly configured

This is an agent config verification task — see AGENTS.md for lint and test requirements.
