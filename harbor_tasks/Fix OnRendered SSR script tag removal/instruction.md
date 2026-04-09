# Fix OnRendered SSR Script Tag Removal

## Problem

The `OnRendered` component in `@tanstack/react-router` was rendering an extra `<script>` tag as a sentinel element to track when the route subtree had finished rendering. This script tag was appearing in the server-side rendered (SSR) HTML output, causing:

1. Unnecessary markup in the HTML
2. Potential hydration mismatches
3. Extra bytes in the response

The component should use a `useLayoutEffect` hook instead to detect when rendering completes, without adding any DOM elements.

## Files to Modify

- `packages/react-router/src/Match.tsx` - Main fix location

## What Needs to Change

The `OnRendered` component currently:
- Renders a `<script>` element with a `ref` callback
- Uses the ref to emit the `onRendered` event when the script mounts

It should:
- Return `null` (render nothing)
- Use `useLayoutEffect` to emit the `onRendered` event after the subtree commits
- Accept a `resetKey` prop for proper timing
- Check if running on server and return null early

## Key Implementation Details

1. Import `useLayoutEffect` from `./utils`
2. On server-side, return `null` immediately
3. Use `useLayoutEffect` to track when the location changes
4. Emit the `onRendered` event via `router.emit()` with type `'onRendered'`
5. Track the previous href to avoid duplicate emissions
6. Update the comment to reflect the new implementation approach

## Testing

The existing test in `packages/react-router/tests/Scripts.test.tsx` expects the SSR output to NOT contain an empty `<script></script>` tag. The test expectation was updated from:

```html
<div><div data-testid="root">root</div><div data-testid="index">index</div><script></script><script src="script.js"></script>...</div>
```

to:

```html
<div><div data-testid="root">root</div><div data-testid="index">index</div><script src="script.js"></script>...</div>
```

Run the unit tests with: `pnpm nx run @tanstack/react-router:test:unit -- tests/Scripts.test.tsx`

Build the package with: `pnpm nx run @tanstack/react-router:build`
