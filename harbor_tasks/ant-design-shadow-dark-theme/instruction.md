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

1. **`components/theme/themes/dark/colors.ts`** - Dark theme color generation
2. **`components/theme/themes/default/colors.ts`** - Light theme color generation
3. **`components/theme/themes/ColorMap.ts`** - Color map type definitions
4. **`components/theme/interface/maps/colors.ts`** - Color token interfaces
5. **`components/theme/util/alias.ts`** - Shadow token generation

## Key Insight

The shadow tokens (like `boxShadow`, `boxShadowCard`, `boxShadowSecondary`) are currently hardcoded to use `rgba(0, 0, 0, ...)` values in `alias.ts`. You need to introduce a `colorShadow` token that derives from the theme (dark for light theme, white for dark theme) and use that as the base for all shadow generation.

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

## Requirements

1. Add a `colorShadow` token to the theme that derives appropriate base colors for each theme
2. Update the shadow token generation to use `colorShadow` as the base color
3. Ensure the alpha values are preserved correctly for both themes
4. The fix should work with custom `colorTextBase` values as well

## References

- Related issue: #57493
- The fix involves modifying the color map types and the alias token generation
