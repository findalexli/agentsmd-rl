# Replace webfont with simplified antialiasing-resistant glyphs

## Problem

The icon font used in screenshot tests (`tests/assets/webfont/iconfont.woff2`) uses complex glyph paths derived from GitHub's octicons icon set (circles with plus/minus symbols inside). These detailed shapes are highly susceptible to antialiasing and font-rendering differences across platforms, causing screenshot comparison tests to break whenever a browser engine updates its text rendering.

## Expected Behavior

The font glyphs for `+` (U+2B) and `-` (U+2D) should be replaced with simple filled rectangles. Simple geometric shapes produce consistent rendering across platforms, eliminating antialiasing-driven flakiness.

Additionally:
- A Python script should be created to regenerate the font programmatically (using `fonttools` and `brotli`), so it can be reproduced deterministically rather than depending on external web tools.
- The existing SVG source (`iconfont.svg`) should be updated to match the simplified paths.
- Test expectations that reference the old font's byte size need to be updated to match the smaller generated file.
- The README in the webfont directory should be updated to document the new font design and how to regenerate it. The old documentation references fontello and octicons, which are no longer relevant.

## Files to Look At

- `tests/assets/webfont/` — the font assets directory (SVG source, woff2 binary, README)
- `tests/components/ct-react-vite/tests/route.spec.tsx` — tests that assert on the font file's byte size
- `tests/components/ct-react-vite/src/assets/iconfont.woff2` — copy of the font used by component tests
