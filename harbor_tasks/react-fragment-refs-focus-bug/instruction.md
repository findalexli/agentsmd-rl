# Fragment Refs Focus Handling Bug

## Problem

The `setFocusIfFocusable` function in the React DOM bindings has two bugs related to focus handling:

1. **Delegated focus detection**: When an element delegates focus handling (like a `<label>` element that focuses its associated input), the function returns `false` even though a focus event occurred on a different element. This happens because the current implementation only listens for focus events on the element itself, not at the document level via capture phase.

2. **Already-focused element**: If an element is already focused, `setFocusIfFocusable` incorrectly returns `false` instead of `true`. This causes issues when calling `fragmentInstance.focus()` on a fragment that already has a focused child - it will skip to the next focusable element instead of staying on the current one.

## Files to Modify

- `packages/react-dom-bindings/src/client/ReactFiberConfigDOM.js` - Contains the `setFocusIfFocusable` function

## Expected Behavior

1. When `setFocusIfFocusable` is called on an element that is already the active element, it should return `true` immediately (short-circuit).

2. When focus is delegated (e.g., clicking a label focuses its input), the function should detect this via a document-level capture phase listener and return `true`.

3. Focus on nested elements within a fragment should be correctly detected and preserved.

## Example Scenario

Consider a form with a fragment containing multiple focusable children:

```jsx
<Fragment ref={fragmentRef}>
  <input id="first" />
  <input id="second" />
</Fragment>
```

If "first" is already focused and you call `fragmentRef.current.focus()`, the focus should stay on "first". Currently, it incorrectly moves to "second" because the function doesn't recognize that the first input is already focused.

Similarly, with delegated focus like `<label><input /></label>`, focusing the label should be detected even though the focus event fires on the input, not the label.
