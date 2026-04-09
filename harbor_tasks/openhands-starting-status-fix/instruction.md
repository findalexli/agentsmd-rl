# Fix Status Display: Show 'Starting' on Resume

## Problem

When resuming a conversation in the OpenHands frontend, the status incorrectly displays **"Disconnected"** even though the server correctly returns **"STARTING"**.

### Symptom

During conversation resume, the WebSocket connection may temporarily show as disconnected while the runtime is initializing. The UI should display "Starting" (based on the server's conversation status), but instead shows "Disconnected" (based on the WebSocket connection state).

### Affected Code

The issue is in `frontend/src/utils/status.ts` in the `getStatusCode` function. This function determines what status message to display based on multiple inputs:
- `statusMessage` - message from the server
- `webSocketStatus` - WebSocket connection state (CONNECTED, DISCONNECTED, etc.)
- `conversationStatus` - conversation state from server (STARTING, RUNNING, etc.)
- `runtimeStatus` - runtime state
- `agentState` - agent state

### Root Cause

The function currently checks WebSocket status (DISCONNECTED) **before** checking conversation status (STARTING). This causes the WebSocket state to take precedence over the server's conversation state.

## Your Task

Fix the `getStatusCode` function in `frontend/src/utils/status.ts` to ensure that when `conversationStatus === "STARTING"`, the function returns `I18nKey.COMMON$STARTING` regardless of the WebSocket connection state.

### Requirements

1. Add a check for `conversationStatus === "STARTING"` that returns `I18nKey.COMMON$STARTING`
2. This check must come **before** the WebSocket status checks in the function
3. Include a comment explaining why this priority is necessary (resume process, WebSocket may be temporarily disconnected)
4. Use `I18nKey.COMMON$STARTING` for the return value (not a hardcoded string)
5. Do not change the function signature

### Testing

The repository has existing tests at `frontend/__tests__/utils/status.test.ts` that you should update or ensure still pass. Run `npm run test` in the frontend directory to verify.

### Code Quality

Before submitting:
- Run `npm run lint:fix` in the frontend directory
- Ensure `npm run build` succeeds
- The fix should not break TypeScript compilation
