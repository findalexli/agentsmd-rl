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

- The file responsible for context propagation in Fiber is `packages/react-reconciler/src/ReactFiberNewContext.js`
- Specifically, look at how the reconciler handles context changes when it encounters suspended Suspense boundaries
- The fiber structure around Suspense has a particular shape: SuspenseComponent → child OffscreenComponent → sibling FallbackFragment

## Expected Behavior

Context consumers in the fallback subtree should receive and re-render with updated context values, just like any other committed fibers that are visible to the user.

## Notes

- This bug is more likely to surface when React Compiler is enabled, as it memoizes more aggressively and reduces incidental re-renders
- The workaround has been that other updates (prop changes) flowing into the fallback sidestep the issue, but pure context changes should work correctly
