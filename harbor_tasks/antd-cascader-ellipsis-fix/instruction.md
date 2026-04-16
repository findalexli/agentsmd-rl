# Fix Cascader Menu Item Ellipsis Styles

## Problem

The Cascader component's menu items are not displaying ellipsis correctly for long option labels when the component uses a flex-based layout. Long text labels overflow their containers instead of being truncated with "..." ellipsis.

When text is too long for the available space in a menu column, the text continues beyond the column boundary rather than being cut off with an ellipsis character.

## Relevant Files

- `components/cascader/style/columns.ts` - Contains the CSS-in-JS styling for Cascader menu columns

## Expected Behavior

Long menu item labels must be truncated with ellipsis ("...") when they exceed the available width in the Cascader menu column.

The tests verify specific CSS property requirements for this to work correctly in flex layout. Specifically, tests check that the CSS output contains:
- `minWidth: 0` within the `&-content` style block
- A `maxWidth` property with a positive value within the `&-item` style block (any positive value such as 400, 300, '100%' will satisfy this)
- `textEllipsis` applied within the `&-content` style block (not in the `&-item` block before `&-content`)

The CSS-in-JS style file uses a `textEllipsis` utility from `../../style` that provides `overflow: 'hidden'`, `textOverflow: 'ellipsis'`, `whiteSpace: 'nowrap'` properties.

## Requirements

1. Long text labels must be truncated with ellipsis when they exceed available width
2. The solution should not break existing functionality
3. Follow the existing code patterns in the repository
4. TypeScript file must compile without errors and pass Biome linting/formatting

## Notes

- The CSS-in-JS style definitions are in `components/cascader/style/columns.ts`
- The `textEllipsis` utility is imported from `../../style`
- The component uses design tokens from the Ant Design token system