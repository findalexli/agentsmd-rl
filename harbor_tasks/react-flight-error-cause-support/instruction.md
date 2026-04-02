# Bug Report: React Flight does not preserve error `.cause` chain across server/client boundary

## Problem

When a Server Component throws an error that has a `.cause` property (the standard `Error` cause chaining introduced in ES2022), the cause information is silently dropped during React Flight serialization. This means any debugging context attached via `new Error("msg", { cause: originalError })` is lost by the time the error reaches the client.

This is particularly painful when debugging nested failures in Server Components, where the root cause is wrapped in higher-level errors. Developers relying on `error.cause` for structured error diagnostics get no cause information on the client side.

## Expected Behavior

When a server-side error has a `.cause` property, the full cause chain should be serialized by the Flight server, transmitted in the Flight protocol, and reconstructed on the client so that `error.cause` is available for inspection in dev tools and error boundaries.

## Actual Behavior

The `.cause` property is completely omitted during Flight error serialization. On the client, caught errors have no `.cause`, regardless of what was set on the server.

## Files to Look At

- `packages/react-server/src/ReactFlightServer.js`
- `packages/react-client/src/ReactFlightClient.js`
- `packages/shared/ReactTypes.js`
