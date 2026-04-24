# Image Component Accessibility Enhancement

The Image component has keyboard accessibility issues that prevent keyboard-only users from navigating and interacting with images and previews.

## Current Problems

1. **Image thumbnails show no focus indicator**: When navigating via Tab key, the cover overlay that appears on mouse hover does not appear when the image is keyboard-focused.

2. **Preview operation buttons show no focus indicator**: The close button and navigation arrows in the preview have no visible focus outline.

3. **Preview toolbar buttons show no focus indicator**: Toolbar action buttons (zoom, rotate, etc.) lack focus outlines.

4. **Focus escapes inline previews**: When an image preview is embedded inline rather than modal, keyboard focus can escape outside the preview area.

5. **`focusTrap` prop undocumented**: The preview component has a `focusTrap` prop (introduced in v6.4.0) that is not documented in the API docs.

6. **`@rc-component/image` version too old**: The current version (`~1.8.0`) predates focus trap support, which requires `~1.9.0` or higher.

## Files to Modify

- `components/image/style/index.ts` - CSS-in-JS style definitions
- `components/image/demo/_semantic.tsx` - Semantic demo with inline preview
- `components/image/index.en-US.md` - English API documentation
- `components/image/index.zh-CN.md` - Chinese API documentation
- `package.json` - Dependency version requirements

## Requirements

### 1. Add focus-visible styles for keyboard navigation

The image cover overlay should be visible when users navigate to images via keyboard Tab key, not just on mouse hover. Preview operation buttons (close, navigation arrows) and toolbar buttons (zoom, rotate, etc.) should display visible focus outlines when focused via keyboard.

The style system provides utilities `genFocusOutline` and `genFocusStyle` for focus styling. The compiled style output must include:
- `genFocusOutline` - for operation button focus outlines
- `genFocusStyle` - for component-level focus styling
- `focus-visible` pseudo-class selector - to respond to keyboard focus on the image cover

### 2. Upgrade @rc-component/image dependency

In `package.json`, update `@rc-component/image` from `~1.8.0` to `~1.9.0` (or higher compatible semver range) to support focus trap functionality.

### 3. Document the focusTrap prop

Add the `focusTrap` prop to the API documentation in both languages:

**English** (`components/image/index.en-US.md`):
- Description: "Whether to trap focus within the preview when open"
- Default: `true`
- Version: `6.4.0`
- Applies to: ImagePreviewType and PreviewGroup tables

**Chinese** (`components/image/index.zh-CN.md`):
- Description: "预览打开时是否在预览内捕获焦点"
- Default: `true`
- Version: `6.4.0`
- Applies to: ImagePreviewType and PreviewGroup tables

### 4. Fix inline preview focus behavior

In `components/image/demo/_semantic.tsx`, the inline preview configuration should set `focusTrap: false` to prevent keyboard focus from being trapped within the inline preview, which would interfere with tab navigation through the page.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `eslint (JS/TS linter)`
