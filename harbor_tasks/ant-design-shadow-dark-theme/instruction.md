# Fix Shadow Tokens for Dark Theme

## Problem

The shadow tokens in Ant Design's theme system don't properly adapt to dark themes. In dark mode, shadows are currently rendered using black colors (`rgba(0, 0, 0, ...)`) which are nearly invisible against dark backgrounds. This causes UI elements like Cards with `hoverable` prop to have no visible shadow feedback.

**Expected behavior:**
- Light theme: Shadows should use dark colors (black with varying opacity)
- Dark theme: Shadows should use light colors (white with varying opacity) for visibility

**Current behavior:**
- Both light and dark themes use dark/black shadow colors
- Dark theme shadows are barely visible

## Files to Explore

The theme system is located in `components/theme/`:

1. **`components/theme/interface/maps/colors.ts`** - Contains the `ColorNeutralMapToken` interface
2. **`components/theme/themes/ColorMap.ts`** - Contains the `GenerateNeutralColorMap` type definition
3. **`components/theme/themes/dark/colors.ts`** - Dark theme color generation with `generateNeutralColorPalettes` function
4. **`components/theme/themes/default/colors.ts`** - Light theme color generation with `generateNeutralColorPalettes` function
5. **`components/theme/util/alias.ts`** - Shadow token generation with hardcoded `rgba(0, 0, 0, ...)` values

## Required Changes

The following specific changes must be made to fix this issue:

### 1. Interface Changes

The `ColorNeutralMapToken` interface in `components/theme/interface/maps/colors.ts` must include a `colorShadow` property marked with `@internal`.

### 2. Type Signature Changes

The `GenerateNeutralColorMap` type in `components/theme/themes/ColorMap.ts` must accept a `shadowColor` parameter (optional).

### 3. Color Generation Changes

Both `generateNeutralColorPalettes` functions (in `components/theme/themes/dark/colors.ts` and `components/theme/themes/default/colors.ts`) must:
- Accept a `shadowColor` optional parameter
- Define a `colorShadow` constant that uses the `shadowColor` parameter or falls back to a default
- Return `colorShadow` in the result object

Default values:
- Dark theme: `colorShadow` should default to `'rgba(255, 255, 255, 0.2)'`
- Light theme: `colorShadow` should default to `'#000'`

### 4. Shadow Token Generation Changes

The `alias.ts` file must be updated to derive shadow colors dynamically from the `colorShadow` token:
- Read `colorShadow` from `mergedToken`
- Create a `FastColor` instance from `mergedToken.colorShadow`
- Implement a `getShadowColor` helper function that takes an alpha multiplier and returns the appropriate color string
- All shadow token definitions (`boxShadow`, `boxShadowSecondary`, `boxShadowTertiary`, `boxShadowCard`, `boxShadowDrawerRight`, `boxShadowDrawerLeft`, `boxShadowDrawerUp`, `boxShadowDrawerDown`, `boxShadowPopoverArrow`, `boxShadowTabsOverflowLeft`, `boxShadowTabsOverflowRight`, `boxShadowTabsOverflowTop`, `boxShadowTabsOverflowBottom`) must use `getShadowColor()` instead of hardcoded `rgba(0, 0, 0, ...)` values

## Reproduction

You can verify the issue by checking the shadow tokens in both themes:

```javascript
// Light theme - should use dark shadows
const lightToken = theme.useToken(); // default algorithm
console.log(lightToken.token.boxShadow); // Should contain rgba(0,0,0,...)

// Dark theme - should use light shadows
const darkToken = theme.useToken({ algorithm: theme.darkAlgorithm });
console.log(darkToken.token.boxShadow); // Currently contains rgba(0,0,0,...) but should contain rgba(255,255,255,...)
```

## Related Issue

- Issue #57493
