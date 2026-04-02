# React Flight: Stale Error in Chunk After Reentrant Module Initialization

## Problem

In React's Flight streaming architecture (used for Server Components), there's a crash that can occur when the response stream closes. The Flight client maintains chunks representing pending data, and when a chunk transitions to the "initialized" state, it should have a valid `FlightStreamController` as its `reason` property.

However, when `requireModule` triggers a reentrant `readChunk` call on the same module chunk, the reentrant call can fail and set `chunk.reason` to an error. After the outer `requireModule` succeeds, the chunk transitions to initialized but retains the stale error as `reason`.

When the Flight response stream later closes and iterates all chunks, it expects `reason` on initialized chunks to be a `FlightStreamController`. Since the stale `reason` is an `Error` object instead, calling `chunk.reason.error()` crashes with:

```
TypeError: chunk.reason.error is not a function
```

## Where to Look

The issue is in the Flight client code that handles chunk initialization. Look at:

- `packages/react-client/src/ReactFlightClient.js` - specifically the `initializeModelChunk` and `initializeModuleChunk` functions
- `packages/react-server/src/ReactFlightReplyServer.js` - specifically the `loadServerReference` function

## Expected Behavior

After a chunk is successfully initialized, its `reason` property should be cleared (set to `null`) so that the stream close handler doesn't try to treat a stale error as a controller.

## Note

The reentrancy can occur when module evaluation synchronously triggers `readChunk` on the same chunk — for example, when code called during evaluation tries to resolve the client reference for the module that is currently being initialized.
