# Fix Context Propagation Through Suspense Fallback

When a React Context value changes, the reconciler propagates the change through the fiber tree to find consumers that need to re-render. However, when it encounters a Suspense boundary that is showing its fallback (because the primary children suspended), the current code incorrectly skips the entire subtree.

The problem is in `packages/react-reconciler/src/ReactFiberNewContext.js` in the `propagateContextChanges` function. When it encounters a Suspense component, it either sets `nextFiber = null` (lazy propagation) or `nextFiber = fiber.child` (full propagation). Neither case correctly handles the scenario where the primary children don't exist in the tree (they were discarded on initial mount) but the fallback children ARE visible and may contain context consumers.

The fiber structure is: `SuspenseComponent -> child: OffscreenComponent (primary, hidden) -> sibling: FallbackFragment`. The fix should skip the primary (hidden) subtree and continue propagation into the fallback subtree so its context consumers are marked for re-render.
