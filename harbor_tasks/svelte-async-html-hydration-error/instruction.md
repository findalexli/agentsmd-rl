# Prevent hydration error on async {@html ...}

## Problem

When using an async `{@html ...}` expression (e.g. `{@html await fetchContent()}`) as the sole child of an element, the component fails during hydration. The compiler incorrectly marks the `HtmlTag` node as "controlled" even when the expression is async, but async nodes need proper anchor comments to track their position during hydration. This mismatch causes a hydration error at runtime.

## Expected Behavior

An async `{@html await ...}` expression as the sole child of an element should hydrate correctly without errors. The compiler should only mark `HtmlTag` nodes as controlled when their expression is synchronous — matching the existing behavior for `EachBlock` nodes, which already have this async guard.

## Files to Look At

- `packages/svelte/src/compiler/phases/3-transform/client/visitors/shared/fragment.js` — the `process_children` function that determines whether child nodes are "controlled" during the client transform phase
