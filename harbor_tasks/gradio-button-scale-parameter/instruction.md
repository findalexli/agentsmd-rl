# Fix: Button component ignoring scale parameter

## Problem

The Button component ignores the `scale` parameter when placed inside a `Row`. Setting `scale=0` on a Button (which should make it fit-content width) has no effect -- the button always expands to fill available space with `flex: 1 1 0%`.

This is a regression in Gradio v6 that breaks layout control for buttons within rows.

## Root Cause

In `js/button/Index.svelte`, the `scale` prop is being read from `gradio.props.scale`. However, `scale` is classified as a "shared prop" in the Gradio framework (listed in `allowed_shared_props` in `js/utils/src/utils.svelte.ts`), so it gets routed to `gradio.shared` rather than `gradio.props`. This means `gradio.props.scale` is always `undefined`, and the button element never receives the correct `flex-grow` inline style.

## Expected Fix

The button component should read the `scale` value from the correct location where shared props are stored, and the `scale` field should be removed from `ButtonProps` since it is a shared prop.

## Files to Investigate

- `js/button/Index.svelte` -- where `scale` is passed to the button component
