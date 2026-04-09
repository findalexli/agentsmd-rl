# Fix TimePicker Column Scroll on Touch Devices

## Problem

TimePicker columns cannot be scrolled directly on touch devices (mobile phones, tablets). Users report that scrolling only works after tapping an item first.

## Root Cause

The time panel column CSS in the date-picker component uses `overflowY: 'hidden'` by default and only enables scrolling via a `:hover` pseudo-class:

```css
/* Current behavior - default */
overflowY: 'hidden'

/* Current behavior - only on hover */
'&:hover': {
  overflowY: 'auto',
}
```

Touch devices do not support hover events, so the `overflowY: 'auto'` that enables scrolling is never triggered naturally. The reason scrolling works after tapping is due to the browser's "sticky hover" behavior where a tap briefly triggers `:hover`.

## Your Task

Fix the TimePicker scrolling issue by modifying the time column styles in `components/date-picker/style/panel.ts`:

1. Change the default `overflowY` value from `'hidden'` to `'auto'`
2. Remove the `&:hover` block that toggles `overflowY: 'auto'` (it's no longer needed)

The fix should ensure:
- Time columns can scroll directly on touch devices without requiring a tap first
- The visual appearance remains unchanged (scrollbars are already styled to be subtle)
- No other date picker functionality is affected

## Reference

- The fix involves the `genPanelStyle` function in the style file
- Look for the time column style object around the `timeColumnWidth` property
- The scrollbar styling (`::-webkit-scrollbar`, `scrollbar-width: thin`) is already in place
