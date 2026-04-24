# Fix OnRendered SSR Script Tag

## Problem

In the `@tanstack/router` repository at `/workspace/router`, the `OnRendered` component in the react-router package renders a `<script>` sentinel tag during server-side rendering (SSR). This creates unnecessary DOM markup and causes hydration mismatches, requiring `suppressHydrationWarning` as a workaround.

The SSR test in `packages/react-router/tests/Scripts.test.tsx` currently expects this bare `<script></script>` sentinel in its `toEqual` assertions.

## Symptom

The `OnRendered` component in `packages/react-router/src/Match.tsx` renders a `<script>` element to detect render completion. This results in:

- A `<script></script>` sentinel tag appearing in SSR HTML output
- The use of `suppressHydrationWarning` to mask hydration issues
- Unnecessary DOM nodes in the rendered page

## Expected Behavior

The component should not render any DOM element — it should `return null` instead of producing markup. Render completion should be detected through React hooks rather than a DOM-based sentinel.

The corrected implementation should exhibit the following properties:

- **No script element:** The source file must not contain both `<script` and `suppressHydrationWarning` — the component returns null.
- **Server detection:** On the server, the component should return null immediately. The check `isServer ?? router.isServer` should be used for this.
- **Event emission:** The component must still emit the `onRendered` event on the client via `router.emit` with `{ type: 'onRendered', ...getLocationChangeInfo(...) }`.
- **Layout effect timing:** Event emission should happen through `useLayoutEffect` (importable from `./utils`), with the hook call structured as `useLayoutEffect(() => {`.
- **Change detection:** The event should only fire when the href actually changes. A ref named `prevHrefRef` should be used to track the previous href value.
- **Reset key prop:** The component must accept a `resetKey` prop typed `{ resetKey: number }`. The existing call site `<OnRendered />` should pass `resetKey={resetKey}`, and `resetKey` should be included in the effect's dependency array.

## Other Files to Update

- **SSR test** (`packages/react-router/tests/Scripts.test.tsx`): Remove the bare `<script></script>` sentinel from the `toEqual` assertions. The expected SSR HTML should no longer contain this tag.

- **Solid Router comment** (`packages/solid-router/src/Match.tsx`): Update the comment above OnRendered to reflect the new approach. The updated comment should indicate the component "needs to run" or has "committed" after the route subtree, replacing the old text about "renders a dummy dom element."

## Verification

- `pnpm nx run @tanstack/react-router:build` must exit with code 0
- `pnpm nx run @tanstack/react-router:test:unit -- tests/Scripts.test.tsx` must exit with code 0

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `eslint (JS/TS linter)`
