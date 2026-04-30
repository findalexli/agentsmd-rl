# TUI worker event streaming uses unnecessary HTTP round-trip

## Bug Description

The TUI worker in `packages/opencode/src/cli/cmd/tui/worker.ts` streams server events by creating an SDK client (`createOpencodeClient`) that makes HTTP SSE requests through the local server's fetch handler. Since the worker runs in the same process as the server, this creates an unnecessary serialization/deserialization round-trip: events are published internally, serialized to SSE format, fetched via HTTP, and then deserialized back into event objects.

This architecture causes:
1. **Unnecessary overhead** — events are serialized and deserialized when they could be consumed directly from the internal event bus
2. **Fragile reconnection** — the SSE stream can silently disconnect, requiring a polling retry loop with `sleep(250)` that may miss events
3. **Missing context** — the SSE path doesn't properly set up workspace or instance context, which means workspace-scoped event filtering doesn't work correctly

## Symptoms

The current implementation uses:
- `createOpencodeClient` from `@opencode-ai/sdk/v2` to create an SDK client
- `sdk.event.subscribe` to listen for SSE events over HTTP
- A polling retry loop with `sleep(250)` when connections fail

This should be replaced with direct internal event bus subscription.

## Required Implementation Elements

When fixing this issue, the implementation must use these specific APIs and patterns:

### Required Imports
- `Bus` from the `@/bus` module (for `Bus.subscribeAll` or `Bus.subscribe`)
- `WorkspaceContext` from the `@/control-plane/workspace-context` module
- `WorkspaceID` from the `@/control-plane/schema` module
- `Instance` from the `@/project/instance` module

### Required Event Handling
- The `Bus.InstanceDisposed` event type must be handled to detect when an instance is disposed and manage reconnection
- `GlobalBus.on` from `@/bus/global` must be used for cross-context event forwarding

### Required Cleanup Pattern
- `AbortController` must be used with its `signal` property for cleanup when subscriptions are aborted

### Code Style Constraints (AGENTS.md conventions)
- No `any` type annotations
- Prefer `const` over `let` (minimize mutable variables)
- Avoid `else` statements; use early returns instead
- Avoid `try/catch` blocks; use `.catch()` on promises instead

### Required RPC Methods
All existing RPC methods must remain exported: `fetch`, `snapshot`, `server`, `checkUpgrade`, `reload`, `shutdown`

## Expected Behavior

The worker should subscribe directly to the internal event bus instead of going through the HTTP SSE layer. The implementation must:

1. Import `Bus` from `@/bus` and use it to subscribe to internal events
2. Import `WorkspaceContext` from `@/control-plane/workspace-context` and `WorkspaceID` from `@/control-plane/schema` to set up workspace context from the input
3. Import `Instance` from `@/project/instance` to set up instance context with the directory and bootstrap information
4. Handle `Bus.InstanceDisposed` events for proper reconnection when instances are disposed
5. Use `AbortController` with its `signal` property for cleanup
6. Continue using `GlobalBus.on` for cross-context event forwarding
7. Preserve all RPC method exports (`fetch`, `snapshot`, `server`, `checkUpgrade`, `reload`, `shutdown`)
8. Remove all usage of `createOpencodeClient` and `sdk.event.subscribe`

## Files to Modify

- `packages/opencode/src/cli/cmd/tui/worker.ts` — replace SSE-based event streaming with internal event bus subscription

## Related Modules

- `packages/opencode/src/bus/index.ts` — internal `Bus` module
- `packages/opencode/src/bus/global.ts` — `GlobalBus` for cross-context forwarding
- `packages/opencode/src/control-plane/workspace-context.ts` — workspace context provider
- `packages/opencode/src/control-plane/schema.ts` — `WorkspaceID` type and constructor
- `packages/opencode/src/project/instance.ts` — instance context provider
