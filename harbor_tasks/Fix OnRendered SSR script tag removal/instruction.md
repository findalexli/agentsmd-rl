# Fix OnRendered SSR Script Tag

## Problem

In the `@tanstack/router` repository at `/workspace/router`, the `OnRendered` component in the react-router package produces a `<script>` tag sentinel during server-side rendering. This creates unnecessary DOM markup and causes hydration mismatches between the server-rendered HTML and the client-side React tree. The current code uses `suppressHydrationWarning` as a workaround for these mismatches.

## Symptom

When the react-router package renders pages on the server, the HTML output includes a bare `<script></script>` tag injected by the `OnRendered` component. This sentinel:

- Appears in the SSR HTML output tested in `packages/react-router/tests/Scripts.test.tsx`
- Creates unwanted DOM nodes in the rendered page
- Requires `suppressHydrationWarning` to mask the resulting hydration warnings

## Expected Behavior

The `OnRendered` component should not render any DOM element. Render completion should be detected through the React component lifecycle rather than by inserting DOM-based sentinels. No `<script>` tag should appear in the component's rendered output, and `suppressHydrationWarning` should not be needed.

## Other Files to Update

- **SSR test** (`packages/react-router/tests/Scripts.test.tsx`): The expected SSR HTML in the `toEqual` assertions contains a bare `<script></script>` tag that the sentinel produces. This expected output string must be updated so the test passes once `OnRendered` no longer injects the tag.

- **Solid Router** (`packages/solid-router/src/Match.tsx`): The comment above the `OnRendered` function describes the old behavior where the component "renders a dummy dom element." This comment should be updated to describe the new approach — that the component needs to run after the route subtree has committed below the root layout.

## Verification

- `pnpm nx run @tanstack/react-router:build` must exit with code 0
- `pnpm nx run @tanstack/react-router:test:unit -- tests/Scripts.test.tsx` must exit with code 0

## Code Style Requirements

Your solution will be checked by the repository's existing linters and type checker. All modified files must pass:

- `eslint` (JS/TS linter)
- `tsc` (TypeScript type-check, via the project's test:types target)
