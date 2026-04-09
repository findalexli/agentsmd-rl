# Flight stream crashes with TypeError when closing after reentrant module chunk initialization

## Problem

When a React Flight response stream closes, it crashes with:

```
TypeError: chunk.reason.error is not a function
```

This happens when a client module's evaluation synchronously triggers a reentrant `readChunk` on the same module chunk (e.g., through `captureOwnerStack()` resolving lazy client references). The reentrant call can fail with a TDZ `ReferenceError`, which gets stored as `chunk.reason`. After the outer `requireModule` succeeds and the chunk transitions to the `INITIALIZED` state, the stale `Error` object remains as `chunk.reason`.

When the Flight stream later closes and iterates all chunks, it expects `reason` on initialized chunks to be a `FlightStreamController` (which has an `.error()` method). Since `reason` is actually a stale `Error` object, calling `chunk.reason.error()` throws a `TypeError`.

This scenario is triggered in Next.js SSR when a client module calls an instrumented API like `Math.random()` in module scope, which synchronously invokes `captureOwnerStack()`.

## Expected Behavior

After a chunk is successfully initialized, any stale `reason` from a failed reentrant attempt should be cleared so that the Flight stream can close without crashing.

## Files to Look At

- `packages/react-client/src/ReactFlightClient.js` — `initializeModelChunk` and `initializeModuleChunk` set chunk status to INITIALIZED but don't clear a potentially stale `reason`
- `packages/react-server/src/ReactFlightReplyServer.js` — `loadServerReference` has the same issue when resolving server references
