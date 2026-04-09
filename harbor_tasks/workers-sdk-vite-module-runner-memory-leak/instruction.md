# Fix potential memory leak in module runner callback cleanup

## Problem

In the Vite plugin for Cloudflare Workers, the module runner's callback mechanism can leak memory. When running a development server, if RPC calls between the worker entry and the Durable Object fail, callback entries accumulate in module-scope `Map` objects (`pendingCallbacks` and `callbackResults`) and are never removed.

This can happen during hot module replacement, network disruptions, or runtime errors in the Durable Object. In a long-running dev session, these leaked entries add up.

## Expected Behavior

All callback Map entries should be properly cleaned up regardless of whether the operation succeeds or fails. No entries should remain in either `pendingCallbacks` or `callbackResults` after a call to `runInRunnerObject` completes — whether successfully or with an error.

## Files to Look At

- `packages/vite-plugin-cloudflare/src/workers/runner-worker/module-runner.ts` — Contains `runInRunnerObject` and the `__VITE_RUNNER_OBJECT__` Durable Object class with `executeCallback`
