# Context changes not reaching Suspense fallback consumers

## Problem

When a React context value changes above a `<Suspense>` boundary that is currently showing its fallback content, context consumers inside the fallback do not re-render. They continue displaying the stale context value even though the provider has been updated.

This is especially noticeable when there is a `React.memo` boundary between the context provider and the Suspense boundary, because memo prevents the fallback element references from changing, so there is no incidental re-render to mask the stale value.

For example, given this component tree:

```
<Context.Provider value={value}>
  <MemoizedWrapper>      ← React.memo
    <Suspense fallback={<FallbackWithContextConsumer />}>
      <SuspendingChild />
    </Suspense>
  </MemoizedWrapper>
</Context.Provider>
```

While `SuspendingChild` is suspended and the fallback is visible, updating `value` does not cause `FallbackWithContextConsumer` to re-render with the new value.

## Expected Behavior

Context consumers inside a Suspense fallback should re-render with the updated context value, just like any other context consumer in the committed tree. The fallback is visible to the user and should reflect the current state.

## Files to Look At

- `packages/react-reconciler/src/ReactFiberNewContext.js` — contains the context propagation logic that traverses the fiber tree to find and mark context consumers for re-render when a provider's value changes
