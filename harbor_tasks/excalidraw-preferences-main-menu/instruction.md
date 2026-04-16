# Add Preferences Submenu to Main Menu

The Excalidraw editor needs a new "Preferences" submenu in the main menu to provide quick access to various editor settings. Currently, users cannot easily discover or toggle editor preferences through the main menu.

## Problem Statement

Settings like tool lock, snap mode, grid mode, zen mode, view mode, and element properties are only accessible via keyboard shortcuts or buried in other UI areas. A Preferences submenu should expose these toggles with visual checkbox indicators showing their current state.

## Requirements

When the implementation is complete, the following must be true:

1. **Checkbox Menu Item Component**
   - A checkbox item component must be available for dropdown menus at `packages/excalidraw/components/dropdownMenu/DropdownMenuItemCheckbox.tsx`
   - It must display a checkmark (using `checkIcon`) when an option is enabled and an empty box (using `emptyIcon`) when disabled
   - The component must accept a `checked` prop to determine its visual state
   - It must be attached to the `DropdownMenu` component as `DropdownMenu.ItemCheckbox`

2. **Type Export**
   - The type `DropdownMenuItemProps` must be exported from `packages/excalidraw/components/dropdownMenu/DropdownMenuItem.tsx`

3. **Settings Icon**
   - A `settingsIcon` (representing adjustments/preferences visually with an "adjustments-horizontal" style SVG) must be exported from `packages/excalidraw/components/icons.tsx`

4. **Keyboard Shortcut**
   - The keyboard shortcut system in `packages/excalidraw/actions/shortcuts.ts` must include `"toolLock"` as a named shortcut with the "Q" key (using `getShortcutKey("Q")`)
   - The `ShortcutName` type must include `"toolLock"`

5. **Preferences Component**
   - A `Preferences` component must be exported from `packages/excalidraw/components/main-menu/DefaultItems.tsx`
   - It must display as a nested submenu (using `DropdownMenuSub`) with `settingsIcon` and the label "Preferences"
   - The submenu must expose toggles as these attached subcomponents:
     - `Preferences.ToggleToolLock` - labeled "Tool lock" with the "Q" shortcut displayed
     - `Preferences.ToggleSnapMode`
     - `Preferences.ToggleGridMode`
     - `Preferences.ToggleZenMode`
     - `Preferences.ToggleViewMode`
     - `Preferences.ToggleElementProperties`
   - Each preference item must show its current state via `DropdownMenuItemCheckbox` with a checkbox indicator
   - Items with keyboard shortcuts must display them alongside the label
   - The preferences component must use these toggle actions: `actionToggleGridMode`, `actionToggleObjectsSnapMode`, `actionToggleStats`, `actionToggleZenMode`, `actionToggleViewMode`
   - The `useApp` hook must be imported and used to access and toggle tool lock state

6. **Localization**
   - The English locale file at `packages/excalidraw/locales/en.json` must contain in the `labels` section:
     - `"preferences": "Preferences"` for the menu label
     - `"preferences_toolLock": "Tool lock"` for the tool lock toggle label

7. **Integration**
   - The main menu in `excalidraw-app/components/AppMainMenu.tsx` must render `<MainMenu.DefaultItems.Preferences>` before the theme toggle

## Expected Behavior

When implemented correctly:
- Users will see a "Preferences" item in the main menu with a settings icon
- Clicking it will open a submenu showing all preference toggles
- Each toggle displays a checkbox showing its current state (checked/unchecked)
- The tool lock toggle shows "Q" as its keyboard shortcut
- Toggling an item immediately applies the change

## Implementation Context

The codebase uses these patterns:
- React functional components with hooks
- `createIcon()` helper for creating SVG icons (takes SVG path string as argument)
- `getShortcutKey()` helper for keyboard shortcut formatting
- Actions are executed via `actionManager.executeAction(action)` pattern
- The `useApp()` hook provides access to the app context
- The existing dropdown menu implementation uses a compound component pattern where subcomponents are attached to the main component

See `CLAUDE.md` and `.github/copilot-instructions.md` for coding standards.
