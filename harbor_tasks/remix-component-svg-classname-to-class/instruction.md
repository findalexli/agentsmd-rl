# Fix SVG `className` normalization in `@remix-run/component`

You are working in a clone of the `remix-run/remix` monorepo at
`/workspace/remix`, checked out at the base commit. The package of
interest is `@remix-run/component` under `packages/component/`.

## Background

The `@remix-run/component` package exposes a small VDOM + SSR runtime.
JSX users pass `className="…"` on elements (the standard React-style
prop) and the runtime is supposed to normalize that prop name to the
HTML attribute `class` before writing it to the DOM (in the VDOM diff
path) or to the streamed HTML output (in the SSR `renderToStream` path).

That normalization works correctly for ordinary HTML elements:

```tsx
<div className="card" />        // → <div class="card"></div>   ✅
```

It is **broken for SVG elements**. At the base commit, both runtime
paths only apply the `className → class` mapping when the element is
*not* an SVG element. For SVG, `className` falls through to the
camelCase-to-kebab-case fallback and gets emitted as `class-name`:

```tsx
<svg className="icon" />        // → <svg class-name="icon"></svg>  ❌  (current behavior)
                                // → <svg class="icon"></svg>       ✅  (expected)
```

This affects both the SSR output (server `renderToStream`) and the
client-side DOM diff that `createRoot` uses to update SVG elements after
the first render.

## What to fix

Make `<svg className="icon">` (and any other SVG element with a
`className` prop) render with the standard HTML `class` attribute, in
**both** of the package's prop-name normalization sites:

1. The DOM-property → HTML-attribute normalizer used by the **VDOM diff**
   path (responsible for `createRoot(...).render(...)` updating SVG DOM
   nodes).
2. The attribute-name transformer used by the **SSR streaming renderer**
   (`renderToStream`, exported from `@remix-run/component/server`).

Other camelCase → kebab-case SVG attribute conversions (e.g.
`strokeLinecap` → `stroke-linecap`, `strokeLinejoin` → `stroke-linejoin`)
must continue to work. Attributes that are deliberately preserved in
camelCase on SVG (e.g. `viewBox`) must continue to be preserved. The
only behavior that changes is `className` on SVG.

The non-SVG (HTML) behavior must be unchanged: `<div className="card">`
still produces `<div class="card">`.

## Acceptance criteria

After your fix:

- `renderToStream(<svg viewBox="0 0 24 24" fill="none" className="icon"><path strokeLinecap="round" strokeLinejoin="round" d="m4.5 12.75 6 6 9-13.5" /></svg>)`
  drained to a string must be exactly:

  ```
  <svg viewBox="0 0 24 24" fill="none" class="icon"><path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5"></path></svg>
  ```

  (The output must not contain `class-name` or `classname=` anywhere.)

- After `createRoot(container).render(<svg className="icon" viewBox="0 0 24 24" />)` and `flush()`:
  - `container.querySelector('svg').getAttribute('class')` is `"icon"`.
  - `container.querySelector('svg').getAttribute('class-name')` is `null`.
  - `container.querySelector('svg').getAttribute('classname')` is `null`.
  - `container.querySelector('svg').getAttribute('viewBox')` is `"0 0 24 24"`.

- `<div className="card">hi</div>` rendered via `renderToStream` still
  produces output containing `class="card"` and not `class-name` or
  `classname=`.

- `pnpm --filter @remix-run/component run typecheck` continues to pass.

- `pnpm run changes:validate` continues to pass. (You will need to add
  a change file for this user-facing fix — see "Repository conventions"
  below.)

## Repository conventions

The repository's root `AGENTS.md` documents conventions that apply to
this change. The most relevant ones:

- **Change files**: User-facing changes to a package require a change
  file under `packages/<pkg>/.changes/`. For this v0.x package, a bug
  fix uses the `patch.<short-description>.md` form. Do **not** edit
  existing `packages/component/CHANGELOG.md` entries.
- **Code style**: Prettier with `printWidth: 100`, no semicolons, single
  quotes, 2-space indent. `let` for local variables, `const` only at
  module scope, never `var`. Use `import type { X }` for type-only
  imports.
- **Comments**: Add non-JSDoc comments only when the code is doing
  something surprising; do not restate trivial logic.

## Code Style Requirements

The graded checks invoke the following tools — your fix must pass them
unmodified:

- **TypeScript** (`pnpm --filter @remix-run/component run typecheck`)
- **changes validation** (`pnpm run changes:validate`)

## What is graded

Your work is graded by behavioral tests that exercise both
`renderToStream` (SSR) and `createRoot(...).render(...)` (VDOM diff)
on SVG elements with a `className` prop, plus regression checks on the
HTML path and on the repository's typecheck and change-file validator.
The tests do **not** read the gold patch — they only observe the
runtime behavior, so any fix that satisfies the acceptance criteria
above will pass.
