# Memory Leak in Dynamic Component Switching

## Problem

When dynamically switching between Svelte components (e.g., toggling `<ComponentA />` and `<ComponentB />`), memory usage grows unboundedly. Destroyed component subtrees are never garbage collected, causing a memory leak that becomes severe with repeated switching.

The issue is in the effect destruction cleanup. When `destroy_effect()` tears down an effect, it nulls out references to allow garbage collection — but it misses one field, causing the destroyed effect to retain a reference to its parent boundary. This boundary holds references to component state and child effects, preventing the entire destroyed subtree from being reclaimed.

## Expected Behavior

After a component is destroyed via `destroy_effect()`, all references held by the effect should be cleared so that the garbage collector can reclaim the entire component subtree. Memory usage should stabilize during repeated component switching, not grow without bound.

## Files to Look At

- `packages/svelte/src/internal/client/reactivity/effects.js` — contains `destroy_effect()`, which handles cleanup when effects are destroyed. Look at the section where references are nulled out at the end of the function.
