# Flight Reply: Unvalidated Blob deserialization from FormData

## Problem

In the React Flight reply server (`ReactFlightReplyServer.js`), the `parseModelString` function handles `$B` references to deserialize Blob entries from FormData. However, the `case 'B'` handler does not validate that the backing FormData entry is actually a `Blob`. It retrieves whatever `FormData.get()` returns — which could be a string — and returns it with only a type cast but no runtime check.

This means a malformed payload can store a large string in a FormData slot and reference it via `$B`, bypassing the `bumpArrayCount` size guard that applies to regular string values.

## Expected Behavior

The `$B` handler should validate that the retrieved FormData entry is actually a `Blob` instance before returning it. If the entry is not a Blob (e.g., it's a string), it should throw an error rather than silently returning the wrong type.

## Files to Look At

- `packages/react-server/src/ReactFlightReplyServer.js` — contains `parseModelString` which handles all `$`-prefixed reference types including `$B` for Blob deserialization
- `scripts/error-codes/codes.json` — registry of React error codes for production error messages
