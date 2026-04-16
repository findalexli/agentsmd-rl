# Cascader Menu Item Text Overflow Bug

## Bug Description

The Cascader component's dropdown menu items don't properly truncate long text with ellipsis. When option labels exceed the available width, the text overflows instead of being truncated with "...".

## Expected Behavior

Long text in Cascader menu items should be truncated with ellipsis (...) when the text exceeds the container width, while maintaining proper flexbox layout behavior.

## Technical Background

CSS flexbox text truncation with ellipsis requires specific conditions:
1. The text container element must have `minWidth: 0` to allow it to shrink below its content size
2. The text-overflow properties (overflow: hidden, white-space: nowrap, text-overflow: ellipsis) must be applied to the element that contains the actual text content — not to its parent flex container
3. The menu item container needs a maxWidth constraint to define the truncation boundary

## Task

Fix the text truncation in `components/cascader/style/columns.ts` so that long menu item text displays with ellipsis when it exceeds the available width.