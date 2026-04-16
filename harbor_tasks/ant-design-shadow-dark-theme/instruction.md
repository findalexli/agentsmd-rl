# Fix Shadow Tokens for Dark Theme

## Problem

The shadow tokens in Ant Design's theme system don't properly adapt to dark themes. In dark mode, shadows are currently rendered using hardcoded black colors (`rgba(0, 0, 0, ...)`) which are nearly invisible against dark backgrounds. This causes UI elements like Cards with `hoverable` prop to have no visible shadow feedback.

**Expected behavior:**
- Light theme: Shadows should use dark colors (black with varying opacity: alpha values 0.08, 0.12, 0.16)
- Dark theme: Shadows should use light colors (white with varying opacity derived from `rgba(255, 255, 255, 0.2)`) for visibility

**Current behavior:**
- Both light and dark themes use hardcoded black shadow colors in files like `components/theme/util/alias.ts`
- Dark theme shadows are barely visible because black shadows don't contrast with dark backgrounds

## Required Behavior

After the fix, the theme system should support dynamic shadow colors that adapt based on the theme:

1. **ColorNeutralMapToken interface** (`components/theme/interface/maps/colors.ts`) should include a shadow color token property that is marked with `@internal` documentation

2. **GenerateNeutralColorMap type** (`components/theme/themes/ColorMap.ts`) should accept an optional parameter for specifying the shadow base color in its type signature

3. **Dark theme colors** (`components/theme/themes/dark/colors.ts`):
   - The `generateNeutralColorPalettes` function should accept an optional parameter for the shadow base color with type `string`
   - The function should define a shadow color constant that defaults to `rgba(255, 255, 255, 0.2)` (white-based for visibility on dark backgrounds) when no shadow color is provided
   - The shadow color constant must be returned in the result object

4. **Light theme colors** (`components/theme/themes/default/colors.ts`):
   - The `generateNeutralColorPalettes` function should accept an optional parameter for the shadow base color with type `string`
   - The function should define a shadow color constant that defaults to `#000` (black for visibility on light backgrounds) when no shadow color is provided
   - The shadow color constant must be returned in the result object

5. **Shadow token generation** (`components/theme/util/alias.ts`) should:
   - No longer contain hardcoded `rgba(0, 0, 0, ...)` values for shadow tokens
   - Read the shadow base color from the merged theme token
   - Create a color manipulation instance from the shadow base color to compute derived colors with varying alpha values
   - Use a helper function that takes an alpha multiplier and returns a color string with the appropriate alpha value applied to the shadow base color
   - Use this helper for all shadow token generation with these specific alpha multipliers:
     - 0.08, 0.12, 0.05 for `boxShadow` and `boxShadowSecondary`
     - 0.03, 0.02, 0.02 for `boxShadowTertiary`
     - 0.05 for `boxShadowPopoverArrow`
     - 0.16, 0.12, 0.09 for `boxShadowCard`
     - 0.08 for drawer and tabs overflow shadows

6. The following shadow tokens must be updated to use the dynamic color derivation (no hardcoded black):
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
