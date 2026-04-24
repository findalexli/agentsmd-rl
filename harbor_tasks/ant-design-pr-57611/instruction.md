# Image Preview Mask Closable Not Working

## Problem

The `Image` component's preview feature allows users to configure a `mask` property with options like `enabled` and `blur`. There's also supposed to be a `closable` option that controls whether clicking the preview mask closes the preview.

However, the `mask.closable` configuration is not being respected. Even when setting `preview.mask.closable: false`, clicking the preview mask still closes the preview modal.

## Expected Behavior

When `preview.mask.closable` is set to `false`:
- Clicking on the preview mask should NOT close the preview
- The preview should only close via the close button or other explicit actions

When `preview.mask.closable` is `true` (or not specified):
- Clicking on the preview mask SHOULD close the preview (default behavior)

## Where to Look

The issue is in how the Image component handles preview configuration:
- `components/image/hooks/useMergedPreviewConfig.ts` - The hook that merges preview config
- `components/image/index.tsx` - The Image component
- `components/image/PreviewGroup.tsx` - The PreviewGroup component

The `useMergedMask` hook from `components/_util/hooks` already returns the closable state, but it may not be properly passed through to the preview component.

## Configuration Levels

This feature should work at multiple levels:
1. `Image` component: `<Image preview={{ mask: { closable: false } }} />`
2. `Image.PreviewGroup`: `<Image.PreviewGroup preview={{ mask: { closable: false } }}>`
3. `ConfigProvider`: `<ConfigProvider image={{ preview: { mask: { closable: false } } }}>`

Component-level configuration should override ConfigProvider settings.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `eslint (JS/TS linter)`
