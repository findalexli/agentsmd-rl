# SSR Output Contains Extra Empty Script Tag

## Problem

When server-side rendering a TanStack Router application, the SSR HTML output contains an unexpected empty `<script></script>` tag that serves no purpose in the rendered markup.

## Observed Behavior

When rendering a basic route with SSR, the output includes an extra empty script tag:

```html
<div>
  <div data-testid="root">root</div>
  <div data-testid="index">index</div>
  <script></script>  <!-- This extra empty script tag should not be here -->
  <script src="script.js"></script>
  <script src="script3.js"></script>
</div>
```

The test `should inject scripts in order` in `packages/react-router/tests/Scripts.test.tsx` currently fails because it expects the SSR output without this extra `<script></script>` tag.

## Expected Behavior

The SSR output should not include the extra empty script tag:

```html
<div>
  <div data-testid="root">root</div>
  <div data-testid="index">index</div>
  <script src="script.js"></script>
  <script src="script3.js"></script>
</div>
```

The `should inject scripts in order` test should pass. The component responsible for tracking render completion and firing `onRendered` events should not render any DOM elements that would appear in the SSR output.

In `packages/solid-router/src/Match.tsx`, the comment above the component responsible for tracking render completion must not contain the phrase "renders a dummy dom element".

All unit tests, type checks, builds, and ESLint checks for both `@tanstack/react-router` and `@tanstack/solid-router` must pass.
