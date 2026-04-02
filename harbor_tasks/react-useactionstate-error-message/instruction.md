# Bug Report: useActionState error message references outdated "form state" terminology

## Problem

The `useActionState` hook (formerly `useFormState`) throws an error message that still uses the old "form state" terminology when a developer attempts to update action state during rendering. The error reads `"Cannot update form state while rendering."` which is confusing because the API was renamed from `useFormState` to `useActionState`, and developers using the current API see a reference to a concept ("form state") that no longer matches the hook they're calling.

This stale terminology also appears in React's production error codes, meaning the mismatch surfaces in both development and production builds.

## Expected Behavior

The error message should reference "action state" to match the current `useActionState` API naming, so developers can clearly understand which hook and state the error relates to.

## Actual Behavior

The error message says `"Cannot update form state while rendering."`, using the outdated "form state" wording from the old `useFormState` API.

## Files to Look At

- `packages/react-reconciler/src/ReactFiberHooks.js`
- `packages/react-dom/src/__tests__/ReactDOMForm-test.js`
- `scripts/error-codes/codes.json`
