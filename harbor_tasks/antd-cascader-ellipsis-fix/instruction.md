# Fix Cascader Menu Item Ellipsis Styles

## Problem

The Cascader component's menu items are not displaying ellipsis correctly for long option labels when in a flex layout. Long text labels overflow their containers instead of being truncated with "..." ellipsis.

This issue affects the `Cascader.Panel` component when displaying options with long text labels in constrained-width columns.

## Relevant Files

- `components/cascader/style/columns.ts` - Contains the CSS-in-JS styling for Cascader menu columns

## Expected Behavior

Long menu item labels should be truncated with ellipsis ("...") when they exceed the available width in the Cascader menu column.

## Technical Details

The Cascader uses CSS-in-JS for styling (via `@ant-design/cssinjs`). The relevant style structure is:

- `&-item` - The flex container for each menu item
- `&-content` - The text content wrapper inside each item
- `textEllipsis` - A utility that provides CSS ellipsis properties (`overflow: hidden`, `textOverflow: 'ellipsis'`, `whiteSpace: 'nowrap'`)

## Requirements

1. Ellipsis styles must work correctly in flex layout
2. The fix should not break existing functionality
3. Follow the existing code patterns in the repository

## Notes

- The issue is specifically with how ellipsis styles are applied in a flex container
- Flex items need special handling to properly truncate text
- The `textEllipsis` utility is imported from `../../style`
- The component uses design tokens from the Ant Design token system
