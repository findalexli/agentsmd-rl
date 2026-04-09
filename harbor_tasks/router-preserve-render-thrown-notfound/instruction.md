# Fix: Preserve render-thrown notFound errors

## Problem

When a route component throws `notFound()` without specifying an explicit `routeId`, the error loses its route context when crossing framework error boundaries. This causes the wrong `notFoundComponent` to be rendered — typically falling back to a parent route's component instead of the intended route's component.

## Expected vs Actual Behavior

**Expected:** When a child route component throws `notFound()`, its own `notFoundComponent` should render (if defined), or the nearest ancestor's `notFoundComponent` should handle it in "fuzzy" mode.

**Actual:** The `notFound()` error crosses framework error boundaries without route context, causing the fuzzy matching logic to fail and potentially render the wrong handler.

## Affected Files

The fix needs to be applied to three framework implementations:

1. **packages/react-router/src/Match.tsx** - React error boundary handling
2. **packages/solid-router/src/Match.tsx** - Solid error boundary handling  
3. **packages/solid-router/src/not-found.tsx** - Solid-specific notFound unwrapping
4. **packages/vue-router/src/Match.tsx** - Vue error boundary handling

## Key Locations

In each `Match.tsx`, look for:
- `onCatch` handlers that check `isNotFound(error)` and re-throw
- `fallback` handlers for notFound boundaries

These are where `notFound()` errors are forwarded through the component tree, and where the `routeId` context needs to be preserved.

## Testing

Test files have been updated with two new test cases:
- `component-thrown bare notFound renders current route notFoundComponent`
- `component-thrown bare notFound falls back to nearest ancestor notFoundComponent`

Run tests with:
```bash
pnpm nx run @tanstack/react-router:test:unit -- tests/not-found.test.tsx
pnpm nx run @tanstack/solid-router:test:unit -- tests/not-found.test.tsx
pnpm nx run @tanstack/vue-router:test:unit -- tests/not-found.test.tsx
```

## Context

This is related to the "fuzzy" `notFoundMode` which finds the nearest parent route with a `notFoundComponent`. The mode works correctly when `notFound()` is thrown from loaders (which have explicit route context), but fails when thrown from components during render because the error boundary loses that context.

For Solid specifically, there's an additional complexity: Solid wraps non-Error throws in an Error object and stores the original value in the `cause` property, requiring special handling to unwrap.

## Agent Guidelines

From AGENTS.md:
- Use `pnpm nx run <project>:<target>` for testing (not npx nx)
- In sandbox, run with `CI=1 NX_DAEMON=false pnpm nx run <project>:<target> --outputStyle=stream --skipRemoteCache`
- Run only one Nx command at a time
- Build packages after changes: `pnpm build:all` or `pnpm nx run @tanstack/PKG:build`

From SKILL.md (not-found-and-errors):
- `notFound()` thrown in components interacts with error boundaries
- `notFoundComponent` cannot use `useLoaderData` but can use `useParams`, `useSearch`, `useRouteContext`
- Leaf routes (without children) cannot handle unmatched paths — only parents with `<Outlet>` can
