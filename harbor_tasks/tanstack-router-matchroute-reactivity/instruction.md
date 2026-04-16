# Fix MatchRoute Reactivity in Solid Router

## Problem

The `MatchRoute` component in `@tanstack/solid-router` has a reactivity bug. When using `MatchRoute` with reactive params or when navigating between routes, the component does not update correctly—it gets stuck showing the initial match result.

### Symptoms

1. **Navigation changes don't update MatchRoute**: When using `router.history.push()` to navigate to a matching route, the `MatchRoute` component doesn't re-render to show the new match.

2. **Reactive param changes don't update MatchRoute**: When passing reactive params (Solid signals) to `MatchRoute`, changes to those signals don't trigger re-rendering.

Example problematic usage:

```tsx
function MyComponent() {
  const [postId, setPostId] = createSignal('123')

  return (
    <div>
      <button onClick={() => setPostId('456')}>Change ID</button>
      <MatchRoute to="/posts/$postId" params={{ postId: postId() }}>
        {(match) => match ? <span>Matched: {match.postId}</span> : <span>No match</span>}
      </MatchRoute>
    </div>
  )
}
```

When the button is clicked, the MatchRoute should update to reflect the new postId, but it stays stuck on the initial value.

## File to Modify

- `packages/solid-router/src/Matches.tsx`

## Requirements

1. The fix should make `MatchRoute` properly reactive to both navigation changes and signal updates
2. All existing unit tests for `@tanstack/solid-router` must continue to pass
3. Type tests must pass
4. The build must succeed

## Testing

Run the unit tests for the solid-router package:

```bash
CI=1 NX_DAEMON=false pnpm nx run @tanstack/solid-router:test:unit --outputStyle=stream --skipRemoteCache
```

Run the type tests:

```bash
CI=1 NX_DAEMON=false pnpm nx run @tanstack/solid-router:test:types --outputStyle=stream --skipRemoteCache
```
