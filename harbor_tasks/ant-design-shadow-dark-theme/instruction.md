# Fix Shadow Tokens for Dark Theme

## Problem

The shadow tokens in Ant Design's theme system don't properly adapt to dark themes. In dark mode, shadows are currently rendered using hardcoded black colors (`rgba(0, 0, 0, ...)`) which are nearly invisible against dark backgrounds. This causes UI elements like Cards with `hoverable` prop to have no visible shadow feedback.

**Expected behavior:**
- Light theme: Shadows should use dark colors (black with varying opacity: alpha values 0.08, 0.12, 0.16)
- Dark theme: Shadows should use light colors (white with varying opacity derived from `rgba(255, 255, 255, 0.2)`) for visibility

**Current behavior:**
- Both light and dark themes use hardcoded black shadow colors in files like `components/theme/util/alias.ts`
- Dark theme shadows are barely visible because black shadows don't contrast with dark backgrounds

## Root Cause Analysis

The shadow tokens are defined using hardcoded `rgba(0, 0, 0, ...)` values in the theme alias generation. These tokens include:
- `boxShadow`
- `boxShadowSecondary`
- `boxShadowTertiary`
- `boxShadowCard`
- `boxShadowDrawerRight`
- `boxShadowDrawerLeft`
- `boxShadowDrawerUp`
- `boxShadowDrawerDown`
- `boxShadowPopoverArrow`
- `boxShadowTabsOverflowLeft`
- `boxShadowTabsOverflowRight`
- `boxShadowTabsOverflowTop`
- `boxShadowTabsOverflowBottom`

The system needs a way to:
1. Define a base shadow color in the neutral color map (the `ColorNeutralMapToken` interface)
2. Accept shadow color configuration in the color generation functions (the `GenerateNeutralColorMap` type)
3. Use different defaults for light vs dark themes (`#000` for light, `rgba(255, 255, 255, 0.2)` for dark)
4. Derive shadow colors dynamically using a helper function (e.g., `getShadowColor`) that applies alpha multipliers to the base shadow color

## Required Behavior

After the fix:
- The `ColorNeutralMapToken` interface should have a `colorShadow` property marked as `@internal`
- The `GenerateNeutralColorMap` type should accept an optional `shadowColor` parameter
- Both dark and default theme color generators should accept `shadowColor` parameter and return `colorShadow`
- Shadow colors should be derived from `mergedToken.colorShadow` using `FastColor`
- A `getShadowColor` helper should apply alpha multipliers to generate shadow colors with appropriate opacity
- No shadow token should contain hardcoded `rgba(0, 0, 0, ...)` values

## Files to Explore

The theme system is located in `components/theme/`:

1. **`components/theme/interface/maps/colors.ts`** - Contains the `ColorNeutralMapToken` interface
2. **`components/theme/themes/ColorMap.ts`** - Contains the `GenerateNeutralColorMap` type definition
3. **`components/theme/themes/dark/colors.ts`** - Dark theme color generation
4. **`components/theme/themes/default/colors.ts`** - Light theme color generation
5. **`components/theme/util/alias.ts`** - Shadow token generation

## Reproduction

You can verify the issue by checking the shadow tokens in both themes:

```javascript
// Light theme - should use dark shadows
const lightToken = theme.useToken(); // default algorithm
console.log(lightToken.boxShadow); // Should contain rgba(0,0,0,...)

// Dark theme - should use light shadows
const darkToken = theme.useToken({ algorithm: theme.darkAlgorithm });
console.log(darkToken.boxShadow); // Currently contains rgba(0,0,0,...) but should contain rgba(255,255,255,...)
```

## Related Issue

- Issue #57493
