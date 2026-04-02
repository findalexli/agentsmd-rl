# Bug Report: CommitTreeBuilder crashes with unhelpful error when cloning a nonexistent node

## Problem

In React DevTools' Profiler, the `getClonedNode` helper inside `updateTree` uses `Object.assign({}, nodes.get(id))` to clone a commit tree node. When the requested fiber ID does not exist in the node map, `nodes.get(id)` returns `undefined`, and `Object.assign` silently produces an empty object. This empty object is then treated as a valid `CommitTreeNode`, leading to confusing downstream failures — missing properties, undefined accesses, or incorrect profiler output — with no indication of what actually went wrong.

## Expected Behavior

When `getClonedNode` is called with a fiber ID that does not exist in the commit tree, it should fail immediately with a clear, descriptive error message identifying the missing node and pointing developers toward the root cause.

## Actual Behavior

The function silently clones `undefined` into an empty object, masking the real problem. Downstream code then operates on an invalid node, producing confusing errors or corrupt profiler data far removed from the actual bug.

## Files to Look At

- `packages/react-devtools-shared/src/devtools/views/Profiler/CommitTreeBuilder.js`
