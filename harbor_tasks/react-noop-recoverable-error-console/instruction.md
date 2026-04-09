# React Noop Renderer Silently Swallows Recoverable Errors

## Problem

The `react-noop-renderer` (used for testing React internals) has an `onRecoverableError` callback that silently discards recoverable errors. When a component triggers a recoverable error during concurrent rendering, the error is swallowed instead of being reported. This means tests using the noop renderer pass even when unasserted recoverable errors occur, masking potential issues that would surface in production renderers.

## Expected Behavior

The `onRecoverableError` callback should report recoverable errors via `console.error` so that tests fail unless they explicitly assert those errors. Test files that exercise recoverable error scenarios need to be updated to assert the newly surfaced console errors.

## Files to Look At

- `packages/react-noop-renderer/src/createReactNoop.js` — contains the `onRecoverableError` implementation in the noop renderer
- `packages/react-reconciler/src/__tests__/ReactIncrementalErrorHandling-test.internal.js` — error handling tests that may need updated assertions
- `packages/react-reconciler/src/__tests__/ReactIncrementalErrorReplay-test.js` — error replay tests
- `packages/react-reconciler/src/__tests__/useMemoCache-test.js` — memo cache tests with error scenarios
