# Context consumers inside Suspense fallbacks show stale values

## Problem

When a React context value changes above a Suspense boundary that is currently showing its fallback content, context consumers inside that fallback do not re-render. They continue displaying the old context value even though the provider has been updated.

This is especially likely to manifest when there is a `React.memo` boundary between the context provider and the Suspense boundary, because the memo prevents prop-driven re-renders that would otherwise mask the issue. React Compiler makes this even more common since it memoizes more aggressively.

For example: a loading spinner that reads a theme context will keep showing the old theme even after the user switches themes, as long as the primary content is still suspended.

## Expected Behavior

When a context value changes, all consumers of that context should re-render with the new value — including consumers that are inside the fallback of a currently-suspended Suspense boundary. The fallback is the content that is visible to the user, so it must stay in sync with the current context.

## Files to Look At

- `packages/react-reconciler/src/ReactFiberNewContext.js` — contains `propagateContextChanges`, which traverses the fiber tree to find context consumers and mark them for re-render when a context value changes. The traversal logic for Suspense boundaries is where the bug lives.
