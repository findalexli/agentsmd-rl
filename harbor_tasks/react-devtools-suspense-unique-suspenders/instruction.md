# Bug Report: Suspense node printing omits `hasUniqueSuspenders` property

## Problem

When using React DevTools' utility functions to serialize Suspense nodes into a human-readable string representation (e.g., for snapshot tests or debugging output), the `hasUniqueSuspenders` property is silently dropped from the output. This means that two Suspense nodes that differ only in their `hasUniqueSuspenders` value produce identical string representations, making it impossible to distinguish them in test snapshots or debug logs.

## Expected Behavior

The printed representation of a Suspense node should include all meaningful properties, including `hasUniqueSuspenders`, so that snapshot tests and debug output accurately reflect the full state of the node. For example, a Suspense node with `hasUniqueSuspenders: true` should be visually distinguishable from one with `hasUniqueSuspenders: false`.

## Actual Behavior

The `printSuspense` function only includes the `name` and `rects` properties in its output string. The `hasUniqueSuspenders` property is completely ignored, so the serialized output loses information and snapshot tests cannot catch regressions related to this field.

## Files to Look At

- `packages/react-devtools-shared/src/devtools/utils.js`
