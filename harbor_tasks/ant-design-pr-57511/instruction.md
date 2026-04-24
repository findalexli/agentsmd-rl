# Shadow Tokens Not Visible in Dark Theme

## Problem

Shadow effects on components like Card (with `hoverable` prop), Drawer, and Dropdown are barely visible when using the dark theme algorithm. The shadows appear to use dark colors intended for light backgrounds, making them ineffective on dark backgrounds.

## Expected Behavior

Shadow tokens should automatically adapt their color based on the active theme:
- Light theme: shadows use dark colors for contrast on light backgrounds
- Dark theme: shadows use light colors for visibility on dark backgrounds

The shadow opacity values must be preserved from the original design:
- Primary shadows: use opacity 0.08, 0.12, and 0.05
- Card shadows: use opacity 0.16, 0.12, and 0.09
- Tertiary shadows: use opacity 0.03 and 0.02
- Popover arrow: uses opacity 0.05
- Tabs overflow: uses opacity 0.08

## Technical Context

The shadow tokens are defined in the theme alias module and currently use hardcoded dark color values. The theme system supports:
- Light theme algorithm in the default theme colors module
- Dark theme algorithm in the dark theme colors module
- Color token interfaces in the colors map interface module

The `@ant-design/fast-color` library is available for color manipulation, consistent with existing codebase patterns.

The following shadow-related tokens must be theme-aware: `boxShadow`, `boxShadowCard`, `boxShadowDrawerRight`, `boxShadowDrawerLeft`, `boxShadowDrawerUp`, `boxShadowDrawerDown`, `boxShadowTabsOverflowLeft`, `boxShadowTabsOverflowRight`, `boxShadowTabsOverflowTop`, `boxShadowTabsOverflowBottom`, `boxShadowPopoverArrow`, `boxShadowSecondary`, and `boxShadowTertiary`.

## Requirements

1. The `ColorNeutralMapToken` interface must include a `colorShadow` property that provides the base shadow color for the current theme.

2. The dark theme must define a light-based shadow color so that shadows are visible on dark backgrounds.

3. The default (light) theme must define a dark-based shadow color so that shadows are visible on light backgrounds.

4. The shadow token definitions must use theme-aware shadow colors derived from the theme's `colorShadow` token instead of hardcoded values.

5. The alpha/opacity values for shadow opacity must be preserved from the original design as specified above.

6. The fix must continue using `@ant-design/fast-color` for color manipulation, consistent with existing codebase patterns.

## Verification Criteria

After the fix:
- The `colorShadow` token should be defined in the color map interface
- The dark theme color map should include a light-based `colorShadow` value
- The default theme color map should include a dark-based `colorShadow` value
- Shadow token definitions should derive their colors from the theme's `colorShadow` token
- Alpha values should be preserved in the shadow definitions

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `black (Python formatter)`
- `eslint (JS/TS linter)`
