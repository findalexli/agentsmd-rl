# Bug Report: Debug info pushed twice for array/iterable children in React reconciler

## Problem

When React Server Components return arrays, iterables, or async iterables as children, the debug info (`_debugInfo`) associated with those children is being pushed onto the debug info stack twice. This happens because the reconciler wraps these children in a Fragment fiber and pushes the debug info during Fragment creation, but then pushes it again when processing the array/iterable in `reconcileChildFibers`. The double-push causes duplicate debug info entries to appear on fibers, polluting developer tooling output and potentially causing incorrect owner/source attribution in DevTools.

## Expected Behavior

Debug info from server component payloads should appear exactly once on the resulting fiber tree. When an array or iterable child is wrapped in a Fragment, the debug info should be pushed once during Fragment creation and not again during reconciliation.

## Actual Behavior

Debug info is pushed twice — once when the Fragment fiber is created for the array/iterable child, and again when `reconcileChildFibers` processes the array/iterable type. This results in duplicated debug info entries on child fibers.

## Files to Look At

- `packages/react-reconciler/src/ReactChildFiber.js`
