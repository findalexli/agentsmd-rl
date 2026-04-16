# Fix: Null/Undefined Error in Toast Handlers

## Problem

The toast notification utilities crash when receiving `null` or `undefined` values:

```
TypeError: Cannot read properties of undefined (reading 'length')
    at s (custom-toast-handlers-CpnJSoYh.js:1:77)
```

This error occurs when `calculateToastDuration()` is called with a null or undefined message, as it tries to access `.length` on the message without checking if it exists first. Additionally, `displayErrorToast()` does not handle cases where the error parameter is null or undefined, leaving the UI without a proper error message.

## Files to Modify

1. **`frontend/src/utils/toast-duration.ts`** - The `calculateToastDuration` function needs null/undefined handling
2. **`frontend/src/utils/custom-toast-handlers.tsx`** - The `displayErrorToast` function needs null/undefined handling with a fallback message
3. **`frontend/__tests__/hooks/use-handle-plan-click.test.tsx`** - Hook tests that may need updates
4. **`frontend/__tests__/hooks/use-sandbox-recovery.test.tsx`** - Hook tests that may need updates

## Required Behavior

### In `toast-duration.ts`:

The `calculateToastDuration` function must:
1. Accept `string | null | undefined` as the message type parameter
2. Return `minDuration` (default 5000ms) immediately when the message is null, undefined, or empty
3. Add a guard clause that returns `minDuration` before attempting any string operations on the message

### In `custom-toast-handlers.tsx`:

The `displayErrorToast` function must:
1. Accept `string | null | undefined` as the error type parameter
2. Provide a fallback error message using i18n (the key `STATUS$ERROR` should be used) when the error is null or undefined
3. Use fallback logic to ensure a user-facing error message is always displayed

### In hook test files:

The tests in `use-handle-plan-click.test.tsx` and `use-sandbox-recovery.test.tsx` may require updates to properly mock the i18n system, particularly `initReactI18next` from `react-i18next`.

## Testing Requirements

After making changes, run the following commands in the `frontend` directory. All must pass:

1. `npm run lint` - Linting must pass without errors
2. `npm run typecheck` - TypeScript type checking must pass
3. `npm run build` - Build must succeed
4. `npm run check-translation-completeness` - Translation completeness check must pass
5. `npm run make-i18n` - i18n translation generation must succeed
6. `npm run test -- --run` - All unit tests must pass

Specific test files that must pass include:
- `toast-duration` unit tests
- `custom-toast-handlers` unit tests
- `use-handle-plan-click` hook tests
- `use-sandbox-recovery` hook tests

## Implementation Notes

- The fix should be minimal - add null checks without changing the core reading-speed calculation logic
- Use the existing i18n system for fallback messages by importing from `#/i18n`
- Follow the existing code style in the repository
- Update the type signatures to reflect that null/undefined are now handled
- If tests fail due to missing i18n mocks, add appropriate `initReactI18next` mocks to the test files