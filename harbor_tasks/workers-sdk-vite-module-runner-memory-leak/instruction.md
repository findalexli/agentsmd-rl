# Fix potential memory leak in module runner callback cleanup

## Problem

In the Vite plugin for Cloudflare Workers, the module runner's callback mechanism can leak memory. When running a development server, if RPC calls between the worker entry and the Durable Object fail, callback entries accumulate in module-scope `Map` objects and are never removed.

The relevant code is in `packages/vite-plugin-cloudflare/src/workers/runner-worker/module-runner.ts`, which uses these module-scope variables:

- `pendingCallbacks` — a `Map` that stores pending callbacks keyed by numeric ID
- `callbackResults` — a `Map` that stores callback return values keyed by the same ID
- `nextCallbackId` — a counter incremented to generate unique callback IDs

The `runInRunnerObject` function implements the callback pattern:
1. It gets a unique ID from `nextCallbackId++`
2. It stores the callback with `pendingCallbacks.set(id, callback)`
3. It gets a Durable Object stub via `env.__VITE_RUNNER_OBJECT__.get("singleton")`
4. It calls `stub.executeCallback(id)` — this RPC invokes the callback inside the Durable Object
5. It reads the result from `callbackResults.get(id)` and returns it

The `executeCallback` method lives on the `__VITE_RUNNER_OBJECT__` Durable Object class. It retrieves the callback from `pendingCallbacks`, runs it, and stores the result in `callbackResults`.

**The bug**: When `stub.executeCallback(id)` throws (due to hot module replacement, network disruptions, or runtime errors in the Durable Object), execution of `runInRunnerObject` aborts. The entry stored in `pendingCallbacks` at step 2 is never removed because `executeCallback` never ran. Similarly, any partial entry in `callbackResults` is not cleaned up. In a long-running dev session, these leaked entries accumulate.

## Expected Behavior

All callback Map entries must be properly cleaned up regardless of whether the operation succeeds or fails. No entries should remain in either `pendingCallbacks` or `callbackResults` after a call to `runInRunnerObject` completes — whether successfully or with an error. The cleanup must happen within `runInRunnerObject` itself, so that the function is resilient to failures in the `executeCallback` RPC call.

## Files to Look At

- `packages/vite-plugin-cloudflare/src/workers/runner-worker/module-runner.ts` — Contains `runInRunnerObject`, the `__VITE_RUNNER_OBJECT__` Durable Object class with `executeCallback`, and the module-scope `pendingCallbacks`, `callbackResults`, and `nextCallbackId` variables.
