# NotFound Component Rendering Bug

## Problem

When a route component throws a `notFound()` error, the wrong `notFoundComponent` is being rendered. Instead of rendering the route-specific not-found handler, the router falls back to a parent or root not-found component.

The root cause is that when a `notFound()` error is thrown from a route component, it passes through the framework's error boundary before being handled. During this crossing, the error loses its route context information, so the router cannot match it to the correct route-specific `notFoundComponent`.

## Expected Behavior

When a component within a route throws `notFound()`:
1. The error should be caught by the framework's error boundary
2. The route's own `notFoundComponent` should be rendered (if defined)
3. If no route-specific handler exists, it should bubble up to ancestor routes
4. The error object must preserve the route's identifier through the error boundary

## Implementation Requirements

### React Router

When handling notFound errors in the Match component's error handler, the code must preserve the route identifier on the error object before re-throwing. The current implementation lacks routeId assignment before re-throwing notFound errors.

**Required pattern:** The fix must use `error.routeId ??= matchState.routeId` to assign the route identifier when not already present.

### Solid Router

Solid wraps thrown values in Error objects with the original value stored on a `.cause` property. The implementation must:

1. Export a helper function that:
   - Takes an `error` parameter of type `unknown`
   - Returns `(NotFoundError & { isNotFound: true }) | undefined`
   - Checks if an error is a notFound error, including checking the error's `.cause` property for Solid's wrapped errors
   - Returns the unwrapped notFound error if found, otherwise returns `undefined`

2. In the Match component, use this helper to unwrap errors before handling them, and preserve the route identifier on the error object before re-throwing.

**Required pattern:** The fix must use `const notFoundError = getNotFound(error)` where `getNotFound` is the helper function, and assign `error.routeId` before throwing.

### Vue Router

Vue uses reactivity patterns where state is accessed via `.value`. When handling notFound errors in the Match component, the code must preserve the route identifier on the error object using Vue's reactive state access patterns.

**Required pattern:** The fix must use `error.routeId ??= matchData.value?.routeId` to assign the route identifier when not already present.

## Testing

After fixing, verify that:
1. Route-thrown `notFound()` renders the current route's `notFoundComponent`
2. Existing unit tests still pass
3. TypeScript compilation succeeds
4. ESLint passes
