# Fix error handling in asyncHandler

The `asyncHandler` function doesn't properly handle errors when a **synchronous** function throws. Currently, it only catches async (Promise) rejections.

## The Bug

When a sync handler throws an error:
```javascript
const handler = asyncHandler((req, res) => {
  throw new Error('sync error');
});
```

The error is not caught and passed to `next()`, which means Express error handlers won't receive it.

## The Fix

Wrap the function call in a try-catch so sync errors are also passed to `next()`.

## Files to Modify

- `index.js` - The main asyncHandler implementation

## Requirements

1. Sync errors thrown by the handler must be caught and passed to `next()`
2. Async errors (Promise rejections) must continue to work as before
3. The return value from the handler must still be available (for chaining)
