# Dropdown options list detaches from input on scroll

## Bug Description

When a Gradio `Dropdown` component's options list is open and the user scrolls the page, the floating options panel (rendered with `position: fixed`) stays in its original position instead of following the input element. This causes the dropdown to visually "detach" from its trigger input.

## Reproduction

1. Create a Gradio app with a `Dropdown` component inside a scrollable page (e.g., place content above and below it so the page is taller than the viewport).
2. Click the dropdown to open it.
3. Scroll the page while the dropdown is open.
4. Observe that the options list remains at its original screen position while the input scrolls away.

## Root Cause

The component in `js/dropdown/shared/DropdownOptions.svelte` has a `scroll_listener` that calls `calculate_window_distance()` to recalculate positioning values when the user scrolls. However, the `$effect` block that maps these positioning values to CSS properties (`top`, `bottom`, `max_height`) never re-runs after the scroll handler updates the values.

The component uses Svelte 5 runes mode. Some variables that the `$effect` depends on may not be declared in a way that triggers reactivity, so mutations to them go unnoticed by the effect system.

## Expected Behavior

The dropdown options list should follow the input element when the page is scrolled, staying anchored to it at all times.

## Relevant Files

- `js/dropdown/shared/DropdownOptions.svelte` — the dropdown positioning logic
