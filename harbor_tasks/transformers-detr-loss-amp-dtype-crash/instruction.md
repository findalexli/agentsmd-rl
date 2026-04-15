# Fix error handling in asyncHandler

The `asyncHandler` function in `index.js` doesn't properly handle errors when a **synchronous** function throws. Currently, it only catches async (Promise) rejections.

## The Bug

When a sync handler throws an error:
```javascript
const handler = asyncHandler((req, res) => {
  throw new Error('sync error');
});
```

The error is not caught and passed to `next()`, which means Express error handlers won't receive it. The thrown error escapes the wrapper entirely.

## Files to Modify

- `index.js` - The main asyncHandler implementation

## Requirements

1. Sync errors thrown by the handler must be caught and passed to `next()`, preserving the original error message (e.g. `'sync error'`)
2. Async errors (Promise rejections) must continue to work as before — they should still be caught and forwarded to `next()`
3. The return value from the handler must still be available (for chaining)
4. No thrown error should escape the wrapper uncaught
