# Stale error message in useActionState hook

## Problem

The `useActionState` hook (formerly `useFormState`) throws an error when its dispatch function is called during rendering. However, the error message still refers to "form state" instead of "action state", which is inconsistent with the current API name.

This stale reference also exists in the error codes registry and the corresponding test expectation.

## Expected Behavior

The error message thrown by the action state dispatch function should use the term "action state" to match the current `useActionState` API name. All references to this error — in source code, error code registry, and tests — should be consistent.

## Files to Look At

- `packages/react-reconciler/src/ReactFiberHooks.js` — contains the `dispatchActionState` function that throws the error
- `scripts/error-codes/codes.json` — React's error code registry mapping numeric codes to messages
- `packages/react-dom/src/__tests__/ReactDOMForm-test.js` — test that validates the error message
