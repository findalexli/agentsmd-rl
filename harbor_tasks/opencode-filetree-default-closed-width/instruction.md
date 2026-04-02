# File Tree Panel Opens Too Wide on Fresh Sessions

## Problem

When a user opens the app for the first time (or clears their persisted layout state), the file tree panel is **open by default** and uses the same large default width as the sidebar (344px). This makes the file tree appear disproportionately large compared to the review panel, crowding the main content area.

The expected behavior is:
- The file tree should be **closed by default** in new sessions
- When opened, the file tree should start at its **minimum width** (200px), not the sidebar's width

## Files to investigate

- `packages/app/src/context/layout.tsx` — layout state management; look at the initial store values for `fileTree` and how the default width constant is used throughout the file tree operations (open, close, toggle, setTab, migration logic)
- `packages/app/src/pages/session.tsx` — session page component; the input field loses focus when navigating to a new session without an ID

## Hints

- The layout context uses a single shared width constant for both the sidebar and the file tree. These panels have different natural sizes — the file tree's minimum is much narrower than the sidebar's default.
- The initial `createStore` call around line 230 sets `fileTree.opened: true` — this is where the default-open behavior comes from.
- There's also a width migration path (around line 165) that handles the old 260px width — make sure it migrates to the correct new default.
- The session page should auto-focus the input when there's no active session ID.
