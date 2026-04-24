# Fix Status Display for Conversation Resume

## Problem

When resuming a conversation in OpenHands, the status bar incorrectly displays "Disconnected" even though the server correctly reports that the conversation is "STARTING". This happens because the WebSocket connection is temporarily disconnected during the resume process, and the frontend was checking WebSocket status before checking the conversation status.

## Your Task

Fix the `getStatusCode` function in `frontend/src/utils/status.ts` so that when the server reports `conversationStatus === "STARTING"`, that status is displayed to the user instead of the WebSocket connection state.

The fix should:
1. Add a priority check for `conversationStatus === "STARTING"` in the status logic
2. This check should come BEFORE the WebSocket status check
3. Include the comment `PRIORITY 2.5: Handle conversation starting state` to document this ordering
4. Update the existing tests in `frontend/__tests__/utils/status.test.ts` to reflect the new behavior
5. Add a test case with the description `show Starting when conversation status is STARTING even with disconnected websocket` that verifies the STARTING status takes priority over DISCONNECTED

## Files to Modify

- `frontend/src/utils/status.ts` - Add the priority check for STARTING status
- `frontend/__tests__/utils/status.test.ts` - Update tests to reflect new priority

## Testing

Run the frontend tests to verify your fix:
```bash
cd /workspace/OpenHands/frontend
npm test -- status.test.ts
```

## Symptoms

- User sees "Disconnected" when resuming a conversation
- Server correctly returns "STARTING" but it's not displayed
- The `getStatusCode` function prioritizes WebSocket status over conversation status

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`
- `eslint (JS/TS linter)`
