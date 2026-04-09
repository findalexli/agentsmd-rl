# Fix: Null/Undefined Error in Toast Handlers

## Problem

The toast notification utilities crash when receiving `null` or `undefined` values:

```
TypeError: Cannot read properties of undefined (reading 'length')
    at s (custom-toast-handlers-CpnJSoYh.js:1:77)
```

This error occurs when `calculateToastDuration()` is called with a null or undefined message, as it tries to access `.length` on the message without checking if it exists first.

## Files to Modify

1. **`frontend/src/utils/toast-duration.ts`** - The `calculateToastDuration` function
2. **`frontend/src/utils/custom-toast-handlers.tsx`** - The `displayErrorToast` function

## Required Changes

### In `toast-duration.ts`:

The `calculateToastDuration` function needs to:
1. Accept `string | null | undefined` as the message type
2. Return `minDuration` immediately when message is null/undefined/empty

### In `custom-toast-handlers.tsx`:

The `displayErrorToast` function needs to:
1. Accept `string | null | undefined` as the error type
2. Provide a fallback error message (using i18n) when error is null/undefined

## Testing Requirements

After making changes:
- Run `npm run lint` in the frontend directory
- Run `npm run typecheck` in the frontend directory
- Run `npm run build` in the frontend directory
- Run `npm run test -- --run` in the frontend directory

All commands should pass without errors.

## Implementation Notes

- The fix should be minimal - add null checks without changing the core logic
- Use the existing i18n system for fallback messages
- Follow the existing code style in the repository
- Update the type signatures to reflect that null/undefined are now handled
