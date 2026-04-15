# Handle ServerErrorEvent in OpenHands Frontend

## Problem

The Agent Server sends a `ServerErrorEvent` message over WebSocket connections when server-side errors occur (such as MCP configuration failures). The frontend currently ignores these events — no error banner is displayed, no analytics are tracked, and budget/credit errors from the server go unnoticed.

The existing error handling only recognizes `ConversationErrorEvent`. When a `ServerErrorEvent` arrives, it is treated as a regular event rather than an error, so users see no feedback about the server-side failure.

## Event Schema

The `ServerErrorEvent` has this structure:

- `kind: "ServerErrorEvent"` — discriminator field for type identification
- `source: "environment"` — always this value for server errors
- `code: string` — error code (e.g., `"MCPError"`)
- `detail: string` — human-readable error message

## Expected Behavior

When the frontend receives a `ServerErrorEvent`:

1. **Error banner**: The event's `detail` should be displayed as an error banner, the same way `ConversationErrorEvent` errors are shown today
2. **Analytics**: The error should be tracked via the existing analytics/telemetry pipeline
3. **Budget/credit errors**: If the `detail` indicates a budget or credit error, the corresponding i18n localized message should be shown instead of the raw detail text
4. **Error clearing**: When a non-error event is received after a `ServerErrorEvent`, the error banner should disappear — consistent with how `ConversationErrorEvent` errors are cleared

New tests should be added to verify the `ServerErrorEvent` handling works correctly.

## Verification

Run these commands in the `frontend/` directory:
- `npm run typecheck` — must pass
- `npm run lint` — must pass
- `npm run build` — must pass
- `npx vitest run` — all tests must pass
