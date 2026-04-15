# TUI worker event streaming uses unnecessary HTTP round-trip

## Bug Description

The TUI worker in `packages/opencode/src/cli/cmd/tui/worker.ts` streams server events by creating an SDK client (`createOpencodeClient`) that makes HTTP SSE requests through the local server's fetch handler. Since the worker runs in the same process as the server, this creates an unnecessary serialization/deserialization round-trip: events are published internally, serialized to SSE format, fetched via HTTP, and then deserialized back into event objects.

This architecture causes:
1. **Unnecessary overhead** — events are serialized and deserialized when they could be consumed directly from the internal event bus
2. **Fragile reconnection** — the SSE stream can silently disconnect, requiring a polling retry loop with `sleep(250)` that may miss events
3. **Missing context** — the SSE path doesn't properly set up workspace or instance context, which means workspace-scoped event filtering doesn't work correctly

## Relevant Code

- `packages/opencode/src/cli/cmd/tui/worker.ts` — the `startEventStream` function
- `packages/opencode/src/bus/index.ts` — the internal `Bus` module
- `packages/opencode/src/control-plane/workspace-context.ts` — workspace context provider
- `packages/opencode/src/project/instance.ts` — instance context provider

## Expected Behavior

The worker should subscribe directly to the internal event bus instead of going through the HTTP SSE layer. The subscription must:

1. Use `Bus.subscribeAll` (from `@/bus`) to subscribe to internal events
2. Wrap the subscription in `WorkspaceContext.provide` (from `@/control-plane/workspace-context`) with a `WorkspaceID` value derived from the input
3. Wrap the subscription in `Instance.provide` (from `@/project/instance`) with the directory and `InstanceBootstrap`
4. Handle `Bus.InstanceDisposed` events to properly manage reconnection when instances are disposed
5. Use `AbortController` with a `signal` for cleanup when the subscription is aborted
6. Continue to use `GlobalBus.on` for cross-context event forwarding
7. Keep all RPC methods (`fetch`, `snapshot`, `server`, `checkUpgrade`, `reload`, `shutdown`) intact in the rpc export
8. Remove all calls to `createOpencodeClient` and `sdk.event.subscribe`