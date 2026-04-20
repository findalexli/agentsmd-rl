# MatchRoute component not updating on navigation or reactive param changes

## Problem

The `MatchRoute` component and `useMatchRoute` hook in `@tanstack/solid-router` don't properly react to changes. When navigation occurs or when reactive params change via signals, the component's children get "stuck" showing their initial match result instead of updating.

For example, with this code:

```tsx
const [postId, setPostId] = createSignal('123')

<MatchRoute to="/posts/$postId" params={{ postId: postId() }}>
  {(match) => <span>{match ? match.postId : 'no-match'}</span>}
</MatchRoute>
```

The rendered content stays stuck on the initial value even after:
- Calling `router.history.push('/posts/456')` to navigate
- Calling `setPostId('456')` to change the reactive param

Both function-based children (render props) and plain element children have this issue.

## Required Code Patterns

The fix must ensure the following specific patterns are present in `/workspace/router/packages/solid-router/src/Matches.tsx`:

### useMatchRoute hook

The `opts` parameter must be destructured **inside** the `Solid.createMemo()` callback to ensure reactive tracking. The code must contain:

```
return Solid.createMemo(() => {
  const { pending, caseSensitive, fuzzy, includeSearch, ...rest } = opts
  ...
})
```

### MatchRoute component

The component must contain these specific patterns:

1. `const renderedChild = Solid.createMemo(` - The rendered output must be wrapped in `Solid.createMemo()`
2. `const child = props.children` - This must appear **inside** the `Solid.createMemo()` callback (not before it)
3. `return <>{renderedChild()}</>` - The component must return `renderedChild()` wrapped in a JSX fragment

## Expected Behavior

- When navigation changes the route, `MatchRoute` should re-evaluate its match and update children accordingly
- When reactive props (like params from signals) change, `MatchRoute` should re-evaluate and re-render
- Both function children and plain element children should respond to these changes
- The type checking, build, ESLint, and unit tests for `Matches.test.tsx` should all pass

## Files to Modify

The changes must be made in:
- `/workspace/router/packages/solid-router/src/Matches.tsx`
