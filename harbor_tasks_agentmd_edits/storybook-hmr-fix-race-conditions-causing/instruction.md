# HMR: Fix race conditions causing stale play functions to fire on re-rendered stories

## Problem

When a story has a play function (especially ones that interact with inputs via `userEvent`), saving the story file triggers Hot Module Replacement (HMR) which causes broken state. The old play function continues running against a freshly-mounted component, causing user-event interactions to bleed across renders. Inputs show stale typed text, and the story gets stuck in broken render phases.

The root cause is that on every file save, multiple independent re-render triggers fire simultaneously:

1. The HMR accept callback fires
2. A `STORY_INDEX_INVALIDATED` event fires immediately (leading edge of debounce) and again after the debounce period (trailing edge) — producing two invalidation events for a single save
3. The `STORY_HOT_UPDATED` event is emitted **after** `onStoriesChanged` has already started a new render, which means it cancels the *new* play function instead of the old one

## Expected Behavior

- At most **one** `STORY_INDEX_INVALIDATED` should fire per file save (the trailing-edge debounce, after the index has been fully regenerated)
- The `STORY_HOT_UPDATED` event (which cancels running play functions) must be emitted **before** `onStoriesChanged` / `onGetProjectAnnotationsChanged` start a new render — not after

## Files to Look At

- `code/core/src/core-server/utils/index-json.ts` — debounce configuration for `STORY_INDEX_INVALIDATED` emission
- `code/builders/builder-vite/src/codegen-modern-iframe-script.ts` — Vite HMR codegen: how `STORY_HOT_UPDATED` is emitted relative to `onStoriesChanged`
- `code/builders/builder-vite/src/codegen-project-annotations.ts` — Vite project annotations HMR: needs the same cancel-before-update pattern
- `code/builders/builder-webpack5/templates/virtualModuleModernEntry.js` — Webpack HMR entry: same issue with emit timing

After fixing the code, update the relevant agent instruction files to document any new development workflow guidance that would help contributors working on this codebase (check `.github/copilot-instructions.md` for existing conventions that could be expanded).
