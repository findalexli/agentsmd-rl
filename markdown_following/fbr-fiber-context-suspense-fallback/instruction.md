# Bug: Context value changes don't propagate into Suspense fallback UI

## Problem Description

When a React Context value changes above a Suspense boundary, context consumers inside the Suspense fallback UI do not re-render with the updated value. They continue to display stale context values.

## Symptom

If you have a structure like:
```jsx
<Context.Provider value={value}>
  <Suspense fallback={<FallbackConsumer />}>
    <AsyncContent />
  </Suspense>
</Context.Provider>
```

Where `FallbackConsumer` uses the context via `useContext()`, and:
1. The async content is suspended (so the fallback is showing)
2. The context value changes while the fallback is visible

The `FallbackConsumer` will **not** re-render with the new context value.

## Scope

- The context propagation logic lives in the React reconciler (`react-reconciler` package), specifically in the code that handles propagating context changes through the fiber tree
- Look at how the reconciler handles context changes when it encounters suspended Suspense boundaries — the primary content and fallback content fibers are siblings in the tree, and only the fallback content is visible to the user while suspended
- This bug is more noticeable when `React.memo` wraps the Suspense boundary, because memo prevents the parent from re-rendering and forces the fallback to rely entirely on fiber-level context propagation

## Expected Behavior

Context consumers in the fallback subtree should receive and re-render with updated context values, just like any other committed fibers that are visible to the user.

## Code Style Requirements

- Code must pass ESLint as configured in the repository (run `yarn lint` to verify)
- JavaScript files must parse without syntax errors (`node --check`)

## Notes

- This bug is more likely to surface when React Compiler is enabled, as it memoizes more aggressively and reduces incidental re-renders
- The workaround has been that other updates (prop changes) flowing into the fallback sidestep the issue, but pure context changes should work correctly
