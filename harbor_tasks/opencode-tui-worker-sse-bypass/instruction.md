# TUI worker event streaming uses unnecessary HTTP round-trip

## Bug Description

The TUI worker in `packages/opencode/src/cli/cmd/tui/worker.ts` streams server events by creating an SDK client (`createOpencodeClient`) that makes HTTP SSE requests through the local server's fetch handler. Since the worker runs in the same process as the server, this creates an unnecessary serialization/deserialization round-trip: events are published internally, serialized to SSE format, fetched via HTTP, and then deserialized back into event objects.

This architecture causes:
1. **Unnecessary overhead** — events are serialized and deserialized when they could be consumed directly from the internal event bus
2. **Fragile reconnection** — the SSE stream can silently disconnect, requiring a polling retry loop with `sleep(250)` that may miss events
3. **Missing context** — the SSE path doesn't properly set up `WorkspaceContext` or `Instance` context, which means workspace-scoped event filtering doesn't work correctly

## Relevant Code

- `packages/opencode/src/cli/cmd/tui/worker.ts` — the `startEventStream` function (around line 45)
- `packages/opencode/src/bus/index.ts` — the internal `Bus` module with `subscribeAll` for direct event subscription
- `packages/opencode/src/control-plane/workspace-context.ts` — workspace context provider

## Expected Behavior

The worker should subscribe directly to the internal event bus instead of going through the HTTP SSE layer, properly wrapping the subscription in `WorkspaceContext` and `Instance` context providers.
