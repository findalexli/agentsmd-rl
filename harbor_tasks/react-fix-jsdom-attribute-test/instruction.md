# Bug Report: ReactDOM attribute test inconsistency with JSDOM's setAttribute and Trusted Types

## Problem

The `ReactDOMAttribute-test.js` test suite has inconsistent behavior depending on the `enableTrustedTypesIntegration` feature flag. When testing that objects with invalid `toString` methods (like `TemporalLike`) are properly rejected as DOM attributes, the test has a branching code path that expects different errors in different configurations. This branching masks the real issue: JSDOM's `setAttribute` doesn't behave like real browsers when given values that can't be implicitly stringified, causing the test environment to diverge from production behavior.

Additionally, `CheckStringCoercion.js` contains stale TODO comments suggesting that the DEV warning for attribute string coercion might be unnecessary when Trusted Types integration is enabled, but this reasoning is incorrect — the coercion check is needed regardless.

## Expected Behavior

The test for `TemporalLike` attribute assignment should have a single, consistent expected error regardless of feature flags, and JSDOM should behave consistently with browser `setAttribute` semantics.

## Actual Behavior

The test branches on `enableTrustedTypesIntegration` and `__DEV__`, expecting different errors in different configurations, hiding the JSDOM environment inconsistency.

## Files to Look At

- `packages/react-dom/src/__tests__/ReactDOMAttribute-test.js`
- `packages/shared/CheckStringCoercion.js`
