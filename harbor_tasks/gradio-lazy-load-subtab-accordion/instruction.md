# Lazy load sub-tab and accordion components

## Problem

When a Gradio app uses nested tabs and accordions, **all** components in non-selected sub-tabs and closed accordions are eagerly pre-loaded and pre-rendered at startup. This means selecting a main tab causes every component in every nested sub-tab and accordion under it to be loaded immediately, even if those sub-tabs are not visible and those accordions are closed.

This leads to unnecessary network requests, slower initial renders, and wasted resources — especially in complex apps with many nested layout containers.

## Expected Behavior

- When a tab becomes visible, only the **selected** sub-tab's components should be loaded. Components in unselected sibling sub-tabs should remain lazy until their tab is clicked.
- When an accordion is **closed** (`open=false`), its child components should **not** be pre-loaded. They should only load when the accordion is opened.
- Open accordions and the default/selected tab should continue to load their children normally.

## Implementation Requirements

### In `js/core/src/init.svelte.ts`

The `make_visible_if_not_rendered` function currently recurses into all children unconditionally. Modify it to:

1. Accept an `is_target_node` parameter (boolean) to distinguish when a node is the direct target of visibility vs. being visited through recursion.

2. For **tabs nodes** (`node.type === "tabs"`):
   - Determine the selected tab ID using `node.props.props.selected ?? node.props.props.initial_tabs?.[0]?.id`
   - When iterating over children, only recurse into `tabitem` children (`child.type === "tabitem"`) whose ID matches the selected ID (`child.props.props.id === selectedId` or `child.id === selectedId`)
   - Skip recursing into unselected tab items

3. For **accordion nodes** (`node.type === "accordion"`):
   - When `node.props.props.open === false` and `is_target_node` is false, do not recurse into children (lazy load)
   - When the accordion is open, recurse into children normally using `node.children.forEach`

### In `js/core/src/_init.ts`

The `determine_visible_components` function currently has no accordion-specific handling. Modify it to:

1. Handle `component.type === "accordion"` separately from other component types.
2. Add accordion components to `visible_components` at initial page load.
3. Only call `process_children_visibility` for accordions when `component.props.open !== false`.
