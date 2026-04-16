# Handle -next Suffix Accumulation Bug

## Problem

The Electric SQL TypeScript client's `ShapeStream` class has a bug where retry URLs grow unboundedly when receiving repeated 409 "must-refetch" responses.

### Symptom

When a proxy or CDN strips the `electric-handle` header from 409 responses, the client appends `-next` to the handle as a cache buster. On each retry, this compounds, producing handles like:
- `handle-next`
- `handle-next-next`
- `handle-next-next-next`
- ... and so on

This causes:
1. Exponentially growing URLs
2. Eventual 414 "URI Too Long" HTTP errors
3. Cascading 5xx failures

### Affected Files

- `packages/typescript-client/src/client.ts` — ShapeStream class implementation

### Root Cause

The 409 response handler in `ShapeStream` fabricates a handle by appending `-next` to the existing handle string, rather than using a proper cache-busting mechanism. Two locations are affected:

1. In `#requestShape`: the handle is built by appending `-next` to the existing handle
2. In `fetchSnapshot`: a similar pattern appends `-next` to a fallback handle

Both patterns cause unbounded handle growth on repeated 409 responses.

### Required Fix

The client must eliminate the `-next` suffix fabrication and instead use a random, one-shot cache-buster mechanism that prevents handle value accumulation across retries.

### Invariants to Maintain

1. Every retry URL must be unique
2. Handles must never be fabricated from existing handles
3. The state machine contract must be preserved
4. Both code paths (`#requestShape` and `fetchSnapshot`) must handle 409 responses correctly
5. TypeScript compilation must pass with no errors
6. The client package must build successfully
7. ESLint style checks must pass
8. Unit tests must pass