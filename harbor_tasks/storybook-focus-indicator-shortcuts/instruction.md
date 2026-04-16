# Fix: Global Shortcuts Not Showing Region Focus Indicator

## Problem

When using global keyboard shortcuts (Alt+A for addon panel, Alt+S for sidebar) in Storybook, the region focus indicator is not shown. However, clicking the buttons to show these panels DOES show the focus indicator correctly.

This is an accessibility issue - users navigating via keyboard don't get the same visual feedback as mouse users.

## Files to Modify

1. `code/core/src/manager-api/modules/shortcuts.ts` - Keyboard shortcut handlers
2. `code/core/src/manager/components/panel/Panel.tsx` - Panel root element ID
3. `code/core/src/manager/components/preview/tools/addons.tsx` - Addon panel button
4. `code/core/src/manager/components/preview/tools/menu.tsx` - Sidebar button

## Required Behavior

### Keyboard Shortcuts

When the keyboard shortcut for toggling the addon panel (Alt+A) fires and the panel becomes visible:
- The focus indicator should be shown for the addon panel region

When the keyboard shortcut for toggling the sidebar (Alt+S) fires and the sidebar becomes visible:
- The focus indicator should be shown for the sidebar region

### Panel Component

The Panel component's root element should use a constant reference for its `id` prop instead of a hardcoded string.

### Button Event Handling

The `showPanel` function in addons.tsx should accept a `forceFocus` parameter of type `boolean` and pass it to `focusOnUIElement`.

The `showSidebar` function in menu.tsx should accept a `forceFocus` parameter of type `boolean` and pass it to `focusOnUIElement`.

Button event handlers should behave as follows:
- `onClick` handler should call the show function with `false` (mouse clicks don't need forced focus)
- `onKeyDown` handler (for Enter/Space) should call the show function with `true` (keyboard activation needs forced focus)

### Code Cleanup

Remove any imports or usage of `useRegionFocusAnimation` from addons.tsx and menu.tsx.

## API Information

The `fullAPI.focusOnUIElement` API accepts an element identifier and an options object. The options object supports:
- `forceFocus: boolean` - Forces the focus animation to show
- `poll: boolean` - Polls for the element if not immediately available

Constants for focusable UI elements:
- `focusableUIElements.addonPanel` - The addon panel region
- `focusableUIElements.sidebarRegion` - The sidebar region
- `focusableUIElements.storyPanelRoot` - The story panel root element

## Testing

After making changes:
1. Ensure TypeScript compilation passes (`yarn nx run-many -t check`)
2. Run unit tests (`yarn test manager-api`)
3. The fix should ensure both mouse clicks AND keyboard shortcuts show the focus indicator
