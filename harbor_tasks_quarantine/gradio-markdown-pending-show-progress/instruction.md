# Bug: `gr.Markdown` shows pending opacity even when `show_progress` is hidden

## Description

When a `gr.Markdown` component is updated via an event listener that has `show_progress="hidden"`, the component still visually dims (drops to 20% opacity) while the update is loading. This defeats the purpose of setting `show_progress` to `"hidden"` — the user expects no visible loading indication at all.

The issue is in the frontend Svelte component at `js/markdown/Index.svelte`. The `pending` CSS class is applied based on the loading status without considering whether progress indication should be shown.

## Expected Behavior

When `show_progress` is set to `"hidden"` on an event that outputs to a Markdown component, no visual loading indicator (including the opacity change) should appear.

When `show_progress` is `"full"` or `"minimal"`, the loading indicator should appear as usual when status is pending.

The fix must maintain backward compatibility: when `show_progress` is undefined/not set, the loading indicator should still appear (preserving existing behavior).

## Actual Behavior

The Markdown content dims to 20% opacity during loading, even when `show_progress="hidden"` is set.

## Relevant Files

- `js/markdown/Index.svelte` — the Markdown component's frontend wrapper

## Code Style Requirements

- This repository uses **tab indentation** for Svelte files. Lines you add or modify must use tab characters for indentation, matching the existing file convention.
- All changes must pass the repository's Prettier format check (`pnpm format:check`).
