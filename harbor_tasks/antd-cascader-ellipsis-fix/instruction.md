# Fix Cascader Menu Item Ellipsis Styles

## Problem

The Cascader component's menu items are not displaying ellipsis correctly for long option labels when in a flex layout. Long text labels overflow their containers instead of being truncated with "..." ellipsis.

This issue affects the Cascader component when displaying options with long text labels in constrained-width columns.

## Relevant Files

- `components/cascader/style/columns.ts` - Contains the CSS-in-JS styling for Cascader menu columns

## Expected Behavior

Long menu item labels should be truncated with ellipsis ("...") when they exceed the available width in the Cascader menu column.

Specifically, the fix must ensure:
1. Menu items have a maximum width of 400 pixels (`maxWidth: 400`) to constrain the flex container
2. The content wrapper inside each menu item has `minWidth: 0` to allow proper text truncation in flex layouts
3. Ellipsis styles are applied to the correct element to prevent text overflow

## Technical Context

The Cascader uses CSS-in-JS for styling via `@ant-design/cssinjs`. The style file imports a `textEllipsis` utility from `../../style` that provides CSS ellipsis properties (`overflow: 'hidden'`, `textOverflow: 'ellipsis'`, `whiteSpace: 'nowrap'`).

## Requirements

1. Ellipsis styles must work correctly in flex layout
2. The fix must include `maxWidth: 400` on menu items to constrain width
3. The fix must include `minWidth: 0` on the content element to allow proper flex shrinking
4. The fix should not break existing functionality
5. Follow the existing code patterns in the repository

## Notes

- Flex items need special handling to properly truncate text - they require both a max-width constraint on the container and `min-width: 0` on the content element
- The component uses design tokens from the Ant Design token system
- Ensure the TypeScript file compiles without errors and passes Biome linting/formatting
