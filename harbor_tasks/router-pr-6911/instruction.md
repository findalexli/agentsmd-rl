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

## Expected Implementation Requirements

To fix this reactivity issue, the following specific changes are required in the `@tanstack/solid-router` package:

### 1. In the `useMatchRoute` hook:

The options parameter destructuring pattern must be moved so it happens inside the `Solid.createMemo()` callback, not before it. This ensures that accesses to the options object (which may contain reactive getters) are tracked by Solid's reactivity system.

The pattern must be:
```
return Solid.createMemo(() => {
  const { pending, caseSensitive, fuzzy, includeSearch, ...rest } = opts
  ...
})
```

### 2. In the `MatchRoute` component:

The component must be restructured with these specific requirements:

- Create a variable named `renderedChild` using `Solid.createMemo(() => { ... })`
- Inside that memo callback, read `props.children` to ensure it's accessed within a tracked scope
- The component's return statement must be: `return <>{renderedChild()}</>`

These specific patterns must appear in the code:
- `const renderedChild = Solid.createMemo(`
- `const child = props.children` (inside the memo callback)
- `return <>{renderedChild()}</>`

## Expected Behavior

- When navigation changes the route, `MatchRoute` should re-evaluate its match and update children accordingly
- When reactive props (like params from signals) change, `MatchRoute` should re-evaluate and re-render
- Both function children and plain element children should respond to these changes
- The type checking, build, ESLint, and unit tests for `Matches.test.tsx` should all pass
