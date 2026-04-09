# Fix: Invert SVGs in Dark Mode

## Problem
SVG images embedded in Excalidraw are not being inverted when the application is in dark mode. This causes white/light SVGs to appear glaring against the dark canvas background, while other elements (shapes, text) properly adapt to the theme.

## Expected Behavior
When Excalidraw is in dark mode (`theme: "dark"`), SVG images should be automatically inverted using the CSS filter `invert(93%) hue-rotate(180deg)`. Non-SVG images (PNGs, JPEGs, etc.) should NOT be inverted, as they may contain photos or graphics that shouldn't be color-adjusted.

## Files to Modify

1. **`packages/common/src/constants.ts`** - Add the `DARK_THEME_FILTER` constant with the filter value

2. **`packages/element/src/renderElement.ts`** - In the `drawElementOnCanvas` function, modify the `"image"` case to:
   - Check if the current theme is dark (`renderConfig.theme === THEME.DARK`)
   - Check if the image is an SVG (`cacheEntry?.mimeType === MIME_TYPES.svg`)
   - Apply `context.filter = DARK_THEME_FILTER` when both conditions are true
   - Use `context.save()` before and `context.restore()` after to isolate the filter

3. **`packages/excalidraw/renderer/staticSvgScene.ts`** - In the SVG export rendering (around line 520), add logic to:
   - Check if the current theme is dark AND the file is an SVG
   - Apply the filter via `g.setAttribute("filter", DARK_THEME_FILTER)` on the group element

## Key Implementation Details

- The filter should ONLY apply to SVGs in dark mode - don't invert PNGs/JPEGs
- The constant `DARK_THEME_FILTER` should be exported from `@excalidraw/common` and imported in both rendering files
- Both canvas rendering and SVG export need to be fixed
- You'll need to import `MIME_TYPES` in `staticSvgScene.ts` for the mime type check

## Testing
Run `yarn test:typecheck` to verify TypeScript compiles without errors after your changes.
