# Lazy load sub-tab and accordion components

## Problem

When a Gradio app uses nested tabs and accordions, **all** components in non-selected sub-tabs and closed accordions are eagerly pre-loaded and pre-rendered at startup. This means selecting a main tab causes every component in every nested sub-tab and accordion under it to be loaded immediately, even if those sub-tabs are not visible and those accordions are closed.

This leads to unnecessary network requests, slower initial renders, and wasted resources — especially in complex apps with many nested layout containers.

## Expected Behavior

- When a tab becomes visible, only the **selected** sub-tab's components should be loaded. Components in unselected sibling sub-tabs should remain lazy until their tab is clicked.
- When an accordion is **closed** (`open=false`), its child components should **not** be pre-loaded. They should only load when the accordion is opened.
- Open accordions and the default/selected tab should continue to load their children normally.

## Files to Look At

- `js/core/src/init.svelte.ts` — Contains `make_visible_if_not_rendered`, the recursive function that makes previously hidden component subtrees visible when a parent container is activated (e.g., tab click). Currently recurses into all children unconditionally.
- `js/core/src/_init.ts` — Contains `determine_visible_components`, which decides which components are visible at initial page load. Handles tabs and tab items but has no specific handling for accordion components.
