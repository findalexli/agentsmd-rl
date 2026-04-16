# Fix DropdownMenu Item Badge Position

## Problem

The badge in dropdown menu items is currently rendered as a child element of the menu item, which causes layout issues. The badge should be rendered in a dedicated position within the menu item content, after the text but before any keyboard shortcut.

## Files to Modify

The following files in `packages/excalidraw/components/` need to be updated:

1. **`dropdownMenu/DropdownMenuItem.tsx`** - Add a `badge` prop to the component interface and pass it to `MenuItemContent`

2. **`dropdownMenu/DropdownMenuItemContent.tsx`** - Accept the `badge` prop and render it in the appropriate position (after the text content, before the shortcut)

3. **`Actions.tsx`** - Move the AI badge from being a child element to the `badge` prop

4. **`FontPicker/FontPickerList.tsx`** - Move the font badge from being a child element to the `badge` prop

5. **`TTDDialog/TTDDialogTrigger.tsx`** - Move the AI badge from being a child element to the `badge` prop

## Expected Behavior

- The `DropdownMenuItem` component should accept an optional `badge` prop of type `React.ReactNode`
- The badge should be rendered in a `div` with class `dropdown-menu-item__badge`
- The badge should appear after the text content but before any keyboard shortcut
- All existing usages of badges in dropdown menu items should be updated to use the new prop instead of rendering as children

## TypeScript Requirements

Ensure all changes maintain type safety and pass `yarn test:typecheck`.

## Hints

- Look at how `MenuItemContent` currently renders its children and where the badge would logically fit in the layout
- The badge prop should be conditionally rendered (only if provided)
- The component already handles `icon`, `shortcut`, and `children` - the `badge` prop follows a similar pattern
