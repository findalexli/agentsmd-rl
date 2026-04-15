# Fix Cascader Menu Item Ellipsis Styles

## Problem Description

The Cascader component's menu items do not correctly display ellipsis for long option labels when used within flex layouts. When option labels exceed the available column width, they should be truncated with an ellipsis (`...`), but instead the text either overflows or the layout breaks.

## Symptom

Long option labels in the Cascader menu do not truncate with ellipsis in flex layouts. Text overflows its container instead of showing "..." for truncated content.

## Relevant Files

- `components/cascader/style/columns.ts` - Contains the CSS-in-JS style definitions for Cascader columns
- The `getColumnsStyle` function within this file handles the column layout styles

## Root Cause

CSS `text-overflow: ellipsis` requires the text element to have a proper width constraint. In CSS flexbox layouts, flex containers do not constrain their children\'s width by default. The ellipsis styles must be applied to the element that directly contains the text, and that element must have `min-width: 0` to allow proper overflow calculation in flex contexts.

## Expected Behavior

After the fix:
1. The `&-item` block should constrain its width appropriately for flex layout
2. The `&-content` block (which holds the text label) should have `min-width: 0` and the ellipsis styles applied to it
3. The `textEllipsis` mixin should be on the text container, not the flex container

## Verification

The fix can be verified by checking:
1. TypeScript compilation succeeds without errors
2. The `textEllipsis` style appears in `&-content` and not in `&-item`
3. The `minWidth: 0` property is present in `&-content`
4. The `maxWidth` property is present in `&-item`
5. The file contains the expected structure (`GenerateStyle`, `CascaderToken`, `getColumnsStyle`)