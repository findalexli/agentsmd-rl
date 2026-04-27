# Storybook HMR: stop stale play functions firing on re-rendered stories

The Storybook preview emits a sequence of channel events on every Hot Module
Replacement (HMR) save. Two of those events have race conditions that cause
play functions from a previous render to keep running into a freshly mounted
story — typing/clicking interactions from the *old* run leak into the *new*
component. Fix the underlying race conditions so that:

1. A single file save triggers exactly one `STORY_INDEX_INVALIDATED` channel
   emit, not two.
2. The `STORY_HOT_UPDATED` channel emit fires synchronously *before* the
   downstream `onStoriesChanged` / `onGetProjectAnnotationsChanged` change
   handler, not after — i.e. **the emit and the change handler must both
   run inside the same HMR `accept` callback, and the emit must come
   first.** The receiver of `STORY_HOT_UPDATED` cancels any in-flight play
   function; emitting it after the new render has already started
   cancels the *new* play function instead of the *old* one.

## Repository layout

You are working in the `storybook` monorepo (Yarn 4 workspaces; root has a
`code/` directory with all source). Paths below are relative to the repo
root. The `storybook` workspace package's `internal/core-events`,
`internal/common`, etc. subpaths are exported from `code/core/`.

## Where the bugs live

There are **four** files that need to change. Each is a small, localised
fix; together they enforce the two contracts above.

### 1. The story-index invalidation route (`code/core/src/core-server/utils/index-json.ts`)

`registerIndexJsonRoute` debounces `channel.emit(STORY_INDEX_INVALIDATED)`
with a 100 ms window. The current debounce configuration is
incompatible with the rest of the server — saving one file produces more
emits than expected. The expected contract: **every emit downstream
of the debounce must correspond to a settled-down burst of changes**, so
that `renderSelection`'s `STORY_UNCHANGED` guard sees a single
post-quiesce signal, not a pre-burst signal that arrives before the new
index is regenerated.

You can see the contract enforced by these two upstream tests in
`code/core/src/core-server/utils/index-json.test.ts`:

- the (modified) `debounces invalidation events` test, which fires bursts
  and asserts the emit count grows by one per burst, and
- the (new) `only emits once per file change (no double-fire from
  leading+trailing edges)` test.

### 2. Three HMR builder entry points

Three files each register an HMR side-channel that emits
`STORY_HOT_UPDATED` (from `storybook/internal/core-events`) at the wrong
moment in the HMR lifecycle — they fire it *outside* the accept callback,
either via a separate `import.meta.hot.on('vite:afterUpdate', …)`
listener, an `import.meta.webpackHot.addStatusHandler('idle', …)`
listener, or not at all. Re-organise each so that the emit is the FIRST
statement *inside* the same `accept` callback that invokes the change
handler:

- **`code/builders/builder-vite/src/codegen-modern-iframe-script.ts`** —
  emits to the storybook preview channel; the matching snapshot tests in
  `codegen-modern-iframe-script.test.ts` encode the new expected
  generated code verbatim.
- **`code/builders/builder-vite/src/codegen-project-annotations.ts`** —
  has TWO branches (CSF4 and non-CSF4); both must emit
  `STORY_HOT_UPDATED` from inside their respective accept callback,
  before invoking `onGetProjectAnnotationsChanged`. The
  `STORY_HOT_UPDATED` constant is currently not in scope in this file.
- **`code/builders/builder-webpack5/templates/virtualModuleModernEntry.js`**
  — has TWO `import.meta.webpackHot.accept(...)` blocks (one for the
  stories file, one for the preview annotations); both must emit
  `STORY_HOT_UPDATED` from the top of their accept callback, before
  invoking the corresponding `preview.onStoriesChanged` /
  `preview.onGetProjectAnnotationsChanged` change handler. The
  `STORY_HOT_UPDATED` constant is already imported at the top of this
  file.

In each of these three files, the *new* `accept`-callback emit replaces
an existing side-channel emit registration; the side-channel registration
must be removed so that exactly one emit fires per HMR update.

## Code Style Requirements

- Any new logging (if any) must use `logger` from
  `storybook/internal/node-logger` (server-side code) or
  `storybook/internal/client-logger` (browser-side code) — not
  `console.log` / `console.warn` / `console.error`.
- All modified `.ts`, `.tsx`, `.js`, `.jsx`, `.mjs`, `.json`, `.html`
  files must pass ESLint (`yarn --cwd code lint:js:cmd <file>`).
- New `vi.mock()` calls (if any) must use the `spy: true` option, be
  placed at the top of the file before any test cases, use `vi.mocked()`
  to access mocked functions, and configure mock behaviour inside
  `beforeEach`. (See `.cursor/rules/spy-mocking.mdc`.)
