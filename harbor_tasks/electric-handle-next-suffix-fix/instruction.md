# Fix: Handle -next suffix accumulation on repeated 409s

## Problem

When the Electric sync server returns a 409 "must-refetch" response, the client fetches a new shape. If the server provides an `electric-handle` header, the client uses it. If not (e.g., a proxy or CDN strips the header), the client may fabricate a new handle by appending `-next` to the current one.

This causes two problems:
1. **Unbounded growth**: Repeated 409s lead to handles like `handle-next-next-next-next...` eventually causing 414 URI Too Long errors
2. **Invalid handles**: When the initial handle was undefined, this produces strings like `undefined-next-next-next...`

## Symptom

After repeated 409 responses from the server, clients experience:
- 414 URI Too Long HTTP errors
- Handles containing `-next` repeated many times
- Valid handles spiraling into invalid URI fragments

## Correct Behavior

- The `-next` suffix pattern must not appear in handle construction code
- When a 409 response lacks a handle header, the client should emit a warning containing: "Received 409 response without a shape handle header" and "proxy or CDN stripping required headers"
- The `#reset()` method must be called in a way that properly handles missing handles (passing `undefined` rather than fabricating a string)
- Retried requests without a handle header must use a unique cache-busting strategy (e.g., query parameter with a time-based + random value) to ensure URL uniqueness

## What to Look For

The fix involves the `ShapeStream` class in `packages/typescript-client/src/client.ts`. Look for code that constructs handles by appending `-next` when processing 409 responses.