# Fix OnRendered SSR Script Tag

## Problem

In the `@tanstack/router` repository at `/workspace/router`, the `OnRendered` component in the react-router package renders a `<script>` sentinel tag that appears in server-side rendered (SSR) HTML output. This creates unnecessary markup and can cause hydration mismatches.

The current implementation renders a `<script>` element with `suppressHydrationWarning` to detect render completion. The SSR test in `Scripts.test.tsx` expects a bare `<script></script>` sentinel tag in the output.

## Required Behavior Changes

### OnRendered Component (`packages/react-router/src/Match.tsx`)

Rewrite the `OnRendered` function so that:

- **No script element is rendered.** The component should return null instead of rendering a `<script>` tag. After the fix, the source file must not contain both `<script` and `suppressHydrationWarning`.

- **Server-side rendering is detected.** On the server, the component should return null immediately. Use the expression `isServer ?? router.isServer` for this check.

- **Render completion is detected via layout effect.** Import `useLayoutEffect` from `'./utils'` and use it to emit the `onRendered` event after mount by calling `router.emit` with `{ type: 'onRendered', ...getLocationChangeInfo(...) }`.

- **Navigation changes are tracked.** Use a ref named `prevHrefRef` to store the previous href value, only emitting the event when the href actually changes.

- **A `resetKey` prop is accepted.** The component should accept `{ resetKey }: { resetKey: number }` and the call site `<OnRendered />` should pass `resetKey={resetKey}`. Include `resetKey` in the effect dependency array.

### SSR Test (`packages/react-router/tests/Scripts.test.tsx`)

Remove the bare `<script></script>` sentinel from the `toEqual` assertions. The expected HTML should no longer contain this sentinel tag.

### Solid Router Comment (`packages/solid-router/src/Match.tsx`)

Update the OnRendered comment to reflect the new approach. It should indicate that the component "needs to run" or has "committed" after the route subtree, replacing the old text about "renders a dummy dom element."

## Verification

- `pnpm nx run @tanstack/react-router:build` must exit with code 0
- `pnpm nx run @tanstack/react-router:test:unit -- tests/Scripts.test.tsx` must exit with code 0
