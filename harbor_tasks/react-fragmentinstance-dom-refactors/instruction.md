# Bug Report: FragmentInstance methods have performance issues and incorrect behavior

## Problem

Several methods on `FragmentInstance.prototype` in the React DOM bindings have performance and correctness issues. The `blur()` method performs a full fragment tree traversal even when the active element isn't contained within the fragment's parent, and it redundantly looks up `ownerDocument.activeElement` on every child node during traversal. The `indexOfEventListener` function calls `normalizeListenerOptions` on the incoming argument repeatedly inside the loop instead of computing it once before iteration, and lacks an early exit for empty arrays. The `compareDocumentPosition` method creates a redundant variable for the first child instance when it already has the value available.

## Expected Behavior

- `blur()` should skip traversal entirely when the active element is not within the fragment's parent element. Text nodes should be skipped since they cannot be focused.
- `indexOfEventListener` should normalize the search options once before the loop and return early for empty arrays.
- `compareDocumentPosition` should not create duplicate instance variables for the same fiber.

## Actual Behavior

- `blur()` always traverses the full fragment tree, doing unnecessary work, and queries `ownerDocument.activeElement` per child.
- `indexOfEventListener` redundantly normalizes options on every iteration.
- `compareDocumentPosition` has a redundant `firstInstance` variable duplicating `firstElement`.

## Files to Look At

- `packages/react-dom-bindings/src/client/ReactFiberConfigDOM.js`
