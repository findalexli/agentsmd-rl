# Disposed virtual roots keep forwarding DOM error events

## Repository layout

You are working inside the `remix-run/remix` monorepo at
`/workspace/remix`. The package you need to fix is
**`@remix-run/component`** at `packages/component`. The relevant module
exports two factory functions:

```ts
import { createRoot, createRangeRoot } from '@remix-run/component'
//                                       (re-exported from src/lib/vdom.ts)
```

Both factories return a "virtual root" — an `EventTarget` that exposes
`render(element)` and `dispose()` (`createRoot` takes an `HTMLElement`,
`createRangeRoot` takes a pair of `[startNode, endNode]` boundary nodes).

## The bug

When a virtual root is created, it attaches a listener for the bubbling
DOM `error` event on the root's container so that DOM-level errors are
re-dispatched on the root's `EventTarget`. **That listener is never
removed when the root is disposed.** As a result, after a caller has
torn the root down with `root.dispose()`, the (still-extant)
`EventTarget` keeps receiving forwarded DOM `error` events from the
container — even though the caller considers the root finished.

Concretely, this is observable as follows:

```ts
import { createRoot } from '@remix-run/component' // src/lib/vdom.ts

let container = document.createElement('div')
let root = createRoot(container)

let forwarded: unknown
root.addEventListener('error', (event) => {
  forwarded = (event as ErrorEvent).error
})

root.dispose()

// After dispose, this event must NOT reach the root listener:
container.dispatchEvent(
  new ErrorEvent('error', { bubbles: true, error: new Error('after dispose') }),
)

// Currently `forwarded` is the dispatched Error.
// After the fix it must be `undefined`.
```

The same problem exists for `createRangeRoot([start, end])`, where the
container is `end.parentNode` (the host that owns the boundary
markers). Disposing a range root must likewise stop forwarding DOM
`error` events bubbling through that host.

## Required behavior

1. **A disposed root must not forward DOM `error` events.** After
   `root.dispose()`, dispatching a bubbling `ErrorEvent` on the
   container (or, for `createRangeRoot`, on the host that owns the
   boundary markers) must not trigger any listeners registered on the
   root via `root.addEventListener('error', ...)`.

2. **Forwarding before dispose must keep working.** Existing event
   forwarding must continue to function for live roots — dispatching a
   bubbling DOM `error` on the container must still reach root
   listeners.

3. **Calling `dispose()` more than once must be safe.** Repeated calls
   to `dispose()` on the same root must not throw.

4. **Reused roots remain functional.** If a root is rendered again
   after being disposed, error forwarding should resume so the reused
   root keeps its expected behavior.

The fix should live in `packages/component/src/lib/vdom.ts` and apply
symmetrically to **both** `createRoot` and `createRangeRoot`.

## Constraints

- Do not change the public API or the signatures of `createRoot` /
  `createRangeRoot`.
- Do not break any of the existing tests in
  `packages/component/src/test/vdom.errors.test.tsx` or
  `packages/component/src/test/vdom.range-root.test.tsx`.
- The `createRoot`/`createRangeRoot` factories already attach their
  forwarding listener as part of construction; preserve that — the fix
  is about lifecycle management of the listener, not about gating
  attachment behind a first `render()`.

## Code Style Requirements

The repo enforces strict style and quality gates. Your patch must
satisfy both:

- **Prettier formatting** — `pnpm --filter @remix-run/component exec
  prettier --check src/lib/vdom.ts` (printWidth 100, no semicolons,
  single quotes, spaces).
- **TypeScript** — `pnpm --filter @remix-run/component exec tsc
  --noEmit` must succeed (strict mode, `verbatimModuleSyntax`, etc.).
- **ESLint** — the repo runs `pnpm run lint` with `--max-warnings=0`
  and the configured rules include `prefer-let` (use `let` for locals,
  `const` only at module scope; never `var`) and `import` plugin
  conventions (use `import type { X }` for type-only imports).
- **Comments** — only add a non-JSDoc comment if the code is doing
  something surprising or non-obvious; don't add narrative comments.

## How to test locally

The component package uses **Vitest in browser mode with Playwright
Chromium**. Chromium is preinstalled in the task environment.

```bash
cd /workspace/remix/packages/component

# Run only the affected files:
pnpm exec vitest run src/test/vdom.errors.test.tsx src/test/vdom.range-root.test.tsx

# Or the whole package:
pnpm exec vitest run

# Typecheck:
pnpm exec tsc --noEmit
```

## Done when

- Disposed `createRoot` and `createRangeRoot` instances no longer
  forward bubbling DOM `error` events to listeners on the root.
- Existing forwarding for live roots, the existing
  `vdom.errors.test.tsx` and `vdom.range-root.test.tsx` suites, and
  the package's typecheck all still pass.
- Repeated `dispose()` calls do not throw.
