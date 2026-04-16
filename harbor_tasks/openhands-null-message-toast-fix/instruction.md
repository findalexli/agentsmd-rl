# Fix Null Message Error in Toast Handlers

## Problem

The application crashes with a TypeError when trying to display toast notifications:

```
TypeError: Cannot read properties of undefined (reading 'length')
    at s (custom-toast-handlers-CpnJSoYh.js:1:77)
    at l (custom-toast-handlers-CpnJSoYh.js:1:276)
```

This error occurs when a toast notification is triggered with a null or undefined error message, specifically in code that attempts to calculate a display duration based on message length.

## Expected Behavior

1. When a toast handler receives a null or undefined message for duration calculation, it should return the minimum duration immediately using a null check pattern like `if (!message)` followed by `return minDuration`.

2. When a toast handler receives a null or undefined error parameter for display, it should fall back to a default translated error message. The translation key to use is `"STATUS$ERROR"`. The fallback should be implemented using the `||` operator pattern: `error || i18n.t("STATUS$ERROR")`.

3. The type signatures for affected functions should accept `string | null | undefined` instead of just `string`.

4. The i18n import should be from `#/i18n`.

## Verification

Before submitting changes, ensure:
- `npm run lint` passes without errors
- `npm run test -- --run` passes
- `npm run build` completes successfully
- `npm run typecheck` passes
- `npm run check-translation-completeness` passes
