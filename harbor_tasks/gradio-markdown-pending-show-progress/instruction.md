# Bug: `gr.Markdown` shows pending opacity even when `show_progress` is hidden

## Description

When a `gr.Markdown` component is updated via an event listener that has `show_progress="hidden"`, the component still visually dims (drops to 20% opacity) while the update is loading. This defeats the purpose of setting `show_progress` to `"hidden"` — the user expects no visible loading indication at all.

The issue is in the frontend Svelte component at `js/markdown/Index.svelte`. The wrapper `<div>` gets a `pending` CSS class applied whenever the loading status is `"pending"`, but the condition doesn't check whether progress indication should actually be shown.

## Expected Behavior

When `show_progress` is set to `"hidden"` on an event that outputs to a Markdown component, no visual loading indicator (including the opacity change) should appear.

## Actual Behavior

The Markdown content dims to 20% opacity during loading, even when `show_progress="hidden"` is set.

## Relevant Files

- `js/markdown/Index.svelte` — the Markdown component's frontend wrapper where the `pending` class is conditionally applied
