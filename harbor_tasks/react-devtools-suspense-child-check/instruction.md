# React DevTools Suspense Child Removal Bug

## Problem

In the React DevTools store, when handling `SUSPENSE_TREE_OPERATION_REMOVE` operations, there's a bug where attempting to remove a suspense node that is **not actually a child** of the specified parent can cause the **wrong node to be silently removed**.

### Location

The issue is in `packages/react-devtools-shared/src/devtools/store.js`, in the section handling suspense tree removal operations (around line 1873).

### Current Behavior

When removing a suspense node from its parent, the code does:

```javascript
const index = parentSuspense.children.indexOf(id);
parentSuspense.children.splice(index, 1);
```

If `id` is not found in `parentSuspense.children`, `indexOf` returns `-1`, and `splice(-1, 1)` removes the **last child in the array** instead of the intended node. This error goes unreported.

### Expected Behavior

Before calling `splice()`, the code should verify that the node ID was actually found in the parent's children array (index !== -1). If not found, it should throw an error using the existing `_throwAndEmitError` pattern, similar to other error checks in the same function.

### Files to Examine

- `packages/react-devtools-shared/src/devtools/store.js` - Look for the `SUSPENSE_TREE_OPERATION_REMOVE` case

### Notes

- The store already has similar error checking for other operations (e.g., "Cannot remove suspense node... no matching node was found")
- The fix should follow the existing error handling patterns in the file
- This is a defensive programming fix - the underlying cause of mismatched IDs may be elsewhere, but the store should fail loudly rather than silently corrupt data
