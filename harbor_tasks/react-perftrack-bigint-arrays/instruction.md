# React Performance Tracks BigInt Array Handling

## Problem

React's performance tracking displays component prop changes in DevTools. When an array contains `BigInt` values (e.g., `[1n, 2n, 3n]`), the code crashes because the system tries to `JSON.stringify` the array, but BigInt is not JSON-serializable.

The issue is in `packages/shared/ReactPerformanceTrackProperties.js` in the `getArrayKind` function. Currently, arrays with BigInt values are incorrectly classified as "primitive only" arrays, which causes them to be passed to `JSON.stringify` and crash.

## Files to Modify

- `packages/shared/ReactPerformanceTrackProperties.js` - The `getArrayKind` function

## Expected Behavior

Arrays containing BigInt values should be treated as "complex" arrays rather than "primitive" arrays. This prevents the crash and displays them as "Array" in the DevTools rather than attempting JSON serialization.

The fix should be minimal - add a check for BigInt values inside the array iteration logic. BigInt can be detected with `typeof value === 'bigint'`.
