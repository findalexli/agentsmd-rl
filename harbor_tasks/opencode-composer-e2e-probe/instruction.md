# Add an e2e composer probe/driver for the todo dock

The Playwright spec at `packages/app/e2e/session/session-composer-dock.spec.ts`
is flaky on the test that exercises todo-dock open/collapse/expand/close
transitions. The test seeds backend todos through the SDK and then races a
mix of `expect.poll(... .count())`, `waitForTimeout`, and DOM visibility
assertions. Because the dock is driven by reactive todo state arriving over
the sync layer (and because the todo lifecycle is itself driven by busy /
blocked / live signals on the composer), the test cannot tell whether the
dock is actually idle, mounted, or hidden — it only sees what landed in the
DOM at a given tick.

You need to make this test deterministic by giving Playwright a way to
**directly drive** the composer state and **directly observe** the todo
dock's render-time state, bypassing the backend sync layer. This is a
test-only seam in app code, plus a rewrite of the flaky spec.

## What to build

### 1. New module: `packages/app/src/testing/session-composer.ts`

A test-only utility module that brokers two channels of state on
`window.__opencode_e2e.composer`:

- **driver state** — set by Playwright, read by the app
- **probe state** — set by the app, read by Playwright

The module **must export exactly the following symbols**:

- A constant `composerEvent` whose value is the literal string
  `"opencode:e2e:composer"`. (Playwright dispatches a `CustomEvent` with
  this name on `window` whenever it pushes a new driver state for a
  session, and the app listens for it.)

- Type `ComposerDriverState` shaped:
  ```ts
  type ComposerDriverState = {
    live?: boolean
    todos?: Array<Pick<Todo, "content" | "status" | "priority">>
  }
  ```
  (`Todo` is imported as a type from `@opencode-ai/sdk/v2`.)

- Type `ComposerProbeState` shaped:
  ```ts
  type ComposerProbeState = {
    mounted: boolean
    collapsed: boolean
    hidden: boolean
    count: number
    states: Todo["status"][]
  }
  ```

- Type `ComposerWindow` — a `Window` extended with an optional
  `__opencode_e2e?: { composer?: { enabled?: boolean; sessions?: Record<string, { driver?: ComposerDriverState; probe?: ComposerProbeState }> } }`.

- A function `composerEnabled()`:
  - Returns `false` when `window` is `undefined` (SSR / pre-mount).
  - Returns `true` only when `window.__opencode_e2e.composer.enabled` is
    strictly equal to `true`. Any falsy or missing value returns `false`.

- A function `composerDriver(sessionID?: string)` that returns the driver
  state for that session, or `undefined`:
  - Returns `undefined` if `sessionID` is missing.
  - Returns `undefined` if `composerEnabled()` is `false`.
  - Returns `undefined` if no driver has been set for that session.
  - Otherwise returns a **shallow clone** of the driver: a new object
    `{ live, todos }` where `todos` is a fresh array of fresh
    `{...todo}` shallow copies (so callers cannot mutate the underlying
    state by mutating the returned value, and vice versa).

- A function `composerProbe(sessionID?: string)` that returns an object
  with two methods, `set(next: ComposerProbeState)` and `drop()`:
  - `set(next)` writes `next` into
    `window.__opencode_e2e.composer.sessions[sessionID].probe`,
    **preserving** any existing `driver` field on that session and
    **cloning** `next.states` into a fresh array (so the writer cannot
    later mutate it through the original reference).
  - `set(next)` is a no-op if `sessionID` is missing or
    `composerEnabled()` is `false`.
  - `drop()` writes a probe of
    `{ mounted: false, collapsed: false, hidden: true, count: 0, states: [] }`.
  - The returned object's methods must close over `sessionID`; calling
    `composerProbe()` with no `sessionID` and then calling `.set(...)`
    must be a safe no-op (no exception, no global write).

The module is test-only, so it must not allocate listeners, intervals, or
reactive subscriptions just by being imported — every code path must be
dormant unless a Playwright fixture has explicitly set
`window.__opencode_e2e.composer.enabled = true`.

### 2. Composer state integration

`packages/app/src/pages/session/composer/session-composer-state.ts` is the
SolidJS reactive state for one session's composer (todos, busy/blocked,
auto-accept, etc.). It builds a `todos` memo that reads from the synced
backend and a `live` memo that combines `busy()` and `blocked()`.

Wire the new driver into this state so that, **only when
`composerEnabled()` is `true`**, the session's effective `todos` and
`live` come from the driver instead of the sync layer:

- On mount, if `composerEnabled()`, read the current driver state for
  `params.id` and stash it in a local reactive store with fields
  `{ on: boolean, live: boolean | undefined, todos: Todo[] | undefined }`.
  (Use `createStore`, not multiple `createSignal` calls — see the
  app's SolidJS guidance.)
- Re-pull the driver state whenever `params.id` changes.
- Listen for the `composerEvent` `CustomEvent` on `window`; when its
  `detail.sessionID` matches `params.id`, re-pull. Clean up the listener
  on unmount.
- The `todos` memo should return the driver's todos when the local
  store's `on` is true and `todos !== undefined`; otherwise the
  pre-existing sync-backed value.
- The `live` memo should likewise prefer the driver's `live` when
  `on === true && live !== undefined`; otherwise the pre-existing
  `busy() || blocked()` value.
- The composer's `clear()` (which empties stale turn todos) must also
  no-op the backend when running under the driver and instead just clear
  the driver-backed todos in the local store.

When `composerEnabled()` is `false`, **none** of this code path may run —
no listeners attached, no extra effects scheduled.

### 3. Todo dock integration

`packages/app/src/pages/session/composer/session-todo-dock.tsx` is the
SolidJS component that renders the dock. Add a new optional `sessionID`
prop and use it to expose the dock's render-time state via the probe:

- On every reactive update, when `composerEnabled()` is `true`, call
  `composerProbe(sessionID).set({...})` with:
    - `mounted: true`
    - `collapsed`: the dock's collapsed flag (true once the user has
      toggled it shut)
    - `hidden`: `collapsed || off`, where `off` is the dock's existing
      "fully hidden" derived signal (the value tracking whether the
      animated hide-progress is essentially complete)
    - `count`: `props.todos.length`
    - `states`: `props.todos.map(t => t.status)` in input order

- On component cleanup (`onCleanup`), when enabled, call
  `composerProbe(sessionID).drop()` so the probe reports `mounted: false`.

### 4. Region wiring

`packages/app/src/pages/session/composer/session-composer-region.tsx`
mounts `SessionTodoDock`. The region currently calls
`useSessionKey()` and destructures only `sessionKey`. Stop destructuring
and keep the full route object, so you can pass `route.params.id` into
the new `sessionID` prop on `SessionTodoDock` and continue using
`route.sessionKey()` everywhere `sessionKey()` was previously used.

### 5. Spec rewrite

In `packages/app/e2e/session/session-composer-dock.spec.ts`, rewrite the
`"todo dock transitions and collapse behavior"` test to use the new
driver/probe instead of `seedSessionTodos` + DOM-only polling. Build a
small fluent helper inside the spec (e.g., `todoDock(page, sessionID)`)
that:

- Installs an `addInitScript` setting
  `window.__opencode_e2e.composer = { enabled: true, sessions: {} }`.
- Provides `open(todos)` / `finish(todos)` / `clear()` that call
  `page.evaluate` to write `composer.sessions[id].driver` and dispatch
  the `composerEvent` `CustomEvent`.
- Provides `expectOpen(states)` / `expectCollapsed(states)` /
  `expectClosed()` that use `expect.poll` against `composer.sessions[id].probe`
  to assert on `{ mounted, collapsed, hidden, count, states }`.
- Provides `collapse()` / `expand()` that click the toggle button.

The new flow should be:

1. Install probe, navigate, wait for the composer dock to be visible.
2. `open([pending, in_progress])` → `expectOpen(["pending", "in_progress"])`.
3. `collapse()` → `expectCollapsed(["pending", "in_progress"])`.
4. `expand()` → `expectOpen(["pending", "in_progress"])`.
5. `finish([completed, cancelled])` → `expectClosed()`.
6. `clear()` in `finally`.

Also factor the four other tests in this spec onto the same idea: add
`expectQuestionBlocked`, `expectQuestionOpen`, `expectPermissionBlocked`,
`expectPermissionOpen` helpers that wait on the dock + prompt visibility
without `expect.poll(... .count())` chains, and have `withMockPermission`
expose a `state.resolved()` awaitable that polls for the mock's
`pending.length === 0` so the permission tests no longer race the
in-flight reply. Drop the now-unused `seedSessionTodos`,
`sessionTodoDockSelector`, and `sessionTodoListSelector` imports. Replace
the `for`-loop-with-`waitForTimeout` body of `clearPermissionDock` with
a single `expect(dock).toBeVisible()` followed by one click.

### 6. Document the rules

Append three new bullet sections to `packages/app/e2e/AGENTS.md` under
the existing "Terminal Tests" section, before the "Writing New Tests"
header. The sections, in order:

- `### Wait on state` — bullets covering: never use `page.waitForTimeout`
  to make a test pass; avoid race-prone flows that assume work is
  finished after an action; wait/poll on observable state with
  `expect(...)`, `expect.poll(...)`, or existing helpers; prefer locator
  assertions like `toBeVisible()`, `toHaveCount(0)`,
  `toHaveAttribute(...)` for normal UI state, and reserve
  `expect.poll(...)` for probe, mock, or backend state.

- `### Add hooks` — bullets covering: when required state isn't
  observable from the UI, add a small test-only driver or probe in app
  code instead of sleeps or fragile DOM checks; keep these hooks minimal
  and purpose-built, following the style of
  `packages/app/src/testing/terminal.ts`; test-only hooks must be inert
  unless explicitly enabled (no normal-runtime listeners, reactive
  subscriptions, or per-update allocations for e2e ceremony); when
  mocking routes or APIs, expose explicit mock state and wait on that
  before asserting post-action UI.

- `### Prefer helpers` — bullets covering: prefer fluent helpers and
  drivers when they make intent obvious and reduce locator-heavy noise;
  use direct locators when the interaction is simple and a helper would
  not add clarity.

## Repo layout

This is a Bun monorepo. The web app lives under `packages/app/`:

- `packages/app/src/testing/` — existing test-only seams in app code
  (e.g., `terminal.ts`); put the new module here.
- `packages/app/src/pages/session/composer/` — composer-related app
  code; that's where the existing `session-composer-state.ts`,
  `session-composer-region.tsx`, and `session-todo-dock.tsx` live.
- `packages/app/e2e/` — Playwright tests, fixtures, selectors, and
  AGENTS.md.

The repo's `tsconfig` resolves `@/` to `packages/app/src/`, so import
the new module from app code as `@/testing/session-composer`. From the
e2e spec file (which lives outside `src/`), use the relative path
`../../src/testing/session-composer`.

## Style

This repo's `AGENTS.md` mandates the following conventions for
agent-written code; follow them in everything you add or touch:

- Single-word names by default for new locals, params, and helpers.
  Multi-word names only when a single word is unclear.
- `const` over `let`; no `else` after `return`; no `try`/`catch` unless
  truly needed.
- Avoid the `any` type. Prefer type inference; only annotate when
  needed for exports or clarity.
- Avoid destructuring `{ a, b }` from objects when you can use
  `obj.a` / `obj.b` and keep context.
- In SolidJS, prefer `createStore` over multiple `createSignal` calls
  for related state.
- Prefer functional array methods (`map` / `filter` / `flatMap`) over
  imperative `for` loops.
