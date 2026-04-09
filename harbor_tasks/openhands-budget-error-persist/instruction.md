# Fix Budget/Credit Error Banner Disappearing Immediately

## Problem

The "Run out of credits" error banner in the OpenHands frontend vanishes approximately 500ms after appearing. This happens because every subsequent non-error WebSocket event clears the error message, even though the user hasn't resolved the underlying budget issue.

## Context

The error handling logic lives in:
- `frontend/src/contexts/conversation-websocket-context.tsx`

This file contains two WebSocket message handlers:
1. `handleMainMessage` - handles events from the main conversation
2. `handlePlanningMessage` - handles events from the planning mode

Both handlers have similar error-clearing logic in their `else` branches that clears the error on any non-error event.

## Root Cause

When a budget/credit error occurs (e.g., `STATUS$ERROR_LLM_OUT_OF_CREDITS`), it's displayed in an error banner. However, the next WebSocket event that arrives (which could be a user message, state update, or any other non-error event) immediately calls `removeErrorMessage()`, causing the banner to disappear before the user can read it.

WebSocket events typically arrive in rapid succession (~500ms apart), so the error is cleared almost immediately.

## Expected Behavior

1. **Budget/credit errors should persist** until there's evidence the LLM is working again
2. **Agent events prove the LLM is working** - when an event with `source: "agent"` arrives, it means credits are available and the budget error should clear
3. **Non-budget errors should continue to clear normally** - on any non-error event, as before

## What You Need to Fix

Modify the error-clearing logic in `conversation-websocket-context.tsx` to:

1. Check if the current error is a budget/credit error (specifically `STATUS$ERROR_LLM_OUT_OF_CREDITS`)
2. Check if the incoming event has `source: "agent"`
3. If it's a budget error AND the event is NOT from an agent, **keep the error visible**
4. Otherwise, clear the error as before

This logic needs to be applied in both `handleMainMessage` and `handlePlanningMessage` handlers.

## Testing

After making changes:

1. Build the frontend: `cd frontend && npm run build`
2. Run linting: `cd frontend && npm run lint`
3. Run tests: `cd frontend && npm run test`

Note: The existing test suite includes tests for this behavior in `frontend/__tests__/conversation-websocket-handler.test.tsx`.

## Hints

- Look for the `removeErrorMessage()` calls in the `else` branches of the message handlers
- Consider extracting a helper function to deduplicate the logic between both handlers
- The error message store can be accessed to check the current error: `useErrorMessageStore.getState().errorMessage`
- The `I18nKey.STATUS$ERROR_LLM_OUT_OF_CREDITS` constant represents the budget error message key
