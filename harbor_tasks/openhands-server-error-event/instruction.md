# Add ServerErrorEvent Handling to OpenHands Frontend

## Problem

The Agent Server has been updated to send a new `ServerErrorEvent` message type over WebSocket connections when server-side errors occur (such as MCP configuration failures). Currently, the frontend does not handle this event type, meaning these errors are silently ignored and users don't see error banners for critical server issues.

## Expected Behavior

When a `ServerErrorEvent` is received:
1. The error should be displayed as a banner to the user (similar to `ConversationErrorEvent`)
2. The error details should be tracked for analytics
3. Budget/credit errors should show the specific i18n message
4. When a non-error event is received afterward, the error banner should clear

## Files to Modify

The main files you'll need to work with are in `frontend/src/`:

1. **`types/v1/core/events/conversation-state-event.ts`** - Add the `ServerErrorEvent` interface definition
2. **`types/v1/type-guards.ts`** - Add type guard functions (`isServerErrorEvent` and `isDisplayableErrorEvent`)
3. **`types/v1/core/openhands-event.ts`** - Add `ServerErrorEvent` to the `OpenHandsEvent` union type
4. **`contexts/conversation-websocket-context.tsx`** - Update error handling to use `isDisplayableErrorEvent` instead of just `isConversationErrorEvent`
5. **`mocks/mock-ws-helpers.ts`** - Add `createMockServerErrorEvent` helper function
6. **`__tests__/conversation-websocket-handler.test.tsx`** - Add tests for ServerErrorEvent handling

## Type Definition Requirements

The `ServerErrorEvent` interface should have:
- `kind: "ServerErrorEvent"` - discriminator field for type guards
- `source: "environment"` - always "environment" for server errors
- `code: string` - error code (e.g., "MCPError")
- `detail: string` - human-readable error message

## Type Guards

Create two new type guards:
1. `isServerErrorEvent(event)` - checks if an event is a ServerErrorEvent
2. `isDisplayableErrorEvent(event)` - checks if an event should display an error banner (returns true for both ConversationErrorEvent and ServerErrorEvent)

## Testing

Your changes should:
- Pass TypeScript type checking (`npm run typecheck`)
- Pass linting (`npm run lint`)
- Include tests that verify ServerErrorEvent handling works correctly

You can verify your implementation by running the frontend tests in the `frontend/` directory.
