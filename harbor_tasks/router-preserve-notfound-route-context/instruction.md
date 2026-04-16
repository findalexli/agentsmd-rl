# Fix: Preserve component-thrown notFound errors

## Problem

When a route component throws a bare `notFound()` call (without specifying a `routeId`), the error loses its route context as it propagates through framework error boundaries. This causes the wrong `notFoundComponent` to render.

### Expected Behavior

When a child route's component throws `notFound()`, that route's own `notFoundComponent` should render (if defined). If not defined, the error should bubble up to the nearest ancestor with a `notFoundComponent`.

### Actual Behavior

The `notFound()` error is caught by framework error boundaries but arrives without a `routeId`. Since the router can't determine which route threw the error, it cannot correctly match the error to the appropriate `notFoundComponent`. This causes:
- Child route's `notFoundComponent` to be skipped even when defined
- Errors to bubble to the root `notFoundComponent` inappropriately

## Requirements

Fix the error handling in all three framework implementations so that `notFound()` errors thrown from route components retain their route context (routeId) when caught in framework error boundaries.

### React Router

In `packages/react-router/src/Match.tsx`, the `ResolvedNotFoundBoundary` component handles notFound errors. When it catches an error, it needs to preserve the routeId from the current match so the error can be routed to the correct `notFoundComponent`.

### Solid Router

Solid has a unique behavior: it wraps non-Error throws in an Error object, storing the original value in a `cause` property. This means when a route component throws `notFound()`, the error boundary may receive a wrapped error.

Two files need changes:
1. `packages/solid-router/src/not-found.tsx` - needs a helper to unwrap Solid's error wrapping
2. `packages/solid-router/src/Match.tsx` - needs to use the helper when handling errors in the notFound boundary

### Vue Router

In `packages/vue-router/src/Match.tsx`, similar to React Router, the notFound error handling needs to preserve the routeId from the current match data.

## Testing

The repository has existing not-found tests. You can run them with:
```bash
pnpm nx run @tanstack/react-router:test:unit -- tests/not-found.test.tsx
pnpm nx run @tanstack/solid-router:test:unit -- tests/not-found.test.tsx
pnpm nx run @tanstack/vue-router:test:unit -- tests/not-found.test.tsx
```

All tests, type checks, and ESLint checks must pass.

## References

- AGENTS.md has detailed instructions on running tests with Nx
- The fix should maintain type safety (TypeScript strict mode)
- All three framework packages need similar but not identical fixes due to framework differences
