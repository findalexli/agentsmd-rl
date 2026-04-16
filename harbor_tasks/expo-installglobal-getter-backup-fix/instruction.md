# Fix installGlobal to Handle Getter Properties Correctly

## Problem

The `installGlobal` function in `packages/expo/src/winter/installGlobal.ts` has a bug in development mode where it creates backup copies of globals (prefixed with `original*`). This causes two issues:

1. **Getter side-effects**: When a property has a getter (lazy initialization), accessing the property to create a backup triggers the getter's side-effect. In React Native's case, this sets `global.URL` back to RN's version.

2. **Enumerable differences**: The backup copies are created as enumerable properties, which makes `Object.keys(global)` return different results in development vs production.

## What You Need to Fix

In the `installGlobal` function, modify the development-mode backup logic so that:

1. **Skip getters**: Properties with getter functions should NOT have backup copies created. The backup property names follow the pattern `original${Name}` (e.g., `originalURL` for `URL`, `originalFetch` for `fetch`). Accessing a getter to create a backup triggers its side-effects, which can revert polyfills.

2. **Make non-enumerable**: Any backup properties that are created must be non-enumerable (should not appear in `Object.keys()` or `for...in` loops), ensuring consistent behavior between development and production environments.

3. **Add explanatory comments**: Include comments explaining why getter properties are excluded from backup creation and why backup properties must be non-enumerable.

## Files to Modify

- `packages/expo/src/winter/installGlobal.ts` - The main source file

## Context

- The `__DEV__` global is a React Native convention indicating development mode
- The backup copies are intended to allow developers to restore original implementations
- This is part of the "winter" polyfill system that provides web-compatible globals in React Native
- The relevant code involves `Object.defineProperty`, `getOwnPropertyDescriptor`, and the `__DEV__` check for backup creation

## Testing Requirements

The fix must:
- Prevent `original*` globals from being created for properties with getters
- Make any created `original*` backups non-enumerable
- Still maintain the development-only backup behavior for regular properties (the `__DEV__` check must remain)
- Pass TypeScript compilation
- Keep the `export function installGlobal` export
