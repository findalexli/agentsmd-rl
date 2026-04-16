# Add closable Support for Image Preview Mask

## Problem

The Image component's preview mask configuration does not expose a way to control whether clicking the mask closes the preview. When users click on the mask/overlay area of an image preview, it currently always closes the preview. Users need the ability to disable this behavior so that clicking the mask does not close the preview.

## Requirements

1. **Image component**: The `preview.mask` configuration should accept a `closable` boolean option that controls whether clicking the mask closes the preview.

2. **Image.PreviewGroup component**: The `preview.mask` configuration should accept a `closable` boolean option with the same pattern as Image.

3. **ConfigProvider**: Should support a global `image.preview.mask.closable` configuration option.

## Technical Requirements

The implementation involves the following components:

### useMergedMask Hook

Located at `components/_util/hooks/useMergedMask.ts`:
- The hook must return a 3-element tuple
- The third element must be a boolean representing the `maskClosable` value (derived from `mask.closable` configuration)
- The return type should be: `[boolean, { mask?: string }, boolean]`

### useMergedPreviewConfig Hook

Located at `components/image/hooks/useMergedPreviewConfig.ts`:
- The hook's return type must include `maskClosable?: boolean` in addition to other properties like `blurClassName`
- The hook must derive the `maskClosable` value from the `mask.closable` configuration and pass it through to the preview component

### Type Definitions

Both `components/image/index.tsx` and `components/image/PreviewGroup.tsx` define an `OriginPreviewConfig` type:
- This type must use an `Omit` pattern to exclude `'maskClosable'` from the base preview config type
- The pattern ensures `maskClosable` is handled internally via `mask.closable` and does not appear as a top-level preview option in the public API

## Mask Configuration Schema

The `mask` property in preview options should support:
- `boolean` — enable/disable mask
- `Object` — with the following optional properties:
  - `enabled?: boolean` — whether the mask is enabled
  - `blur?: boolean` — whether to apply blur effect
  - `closable?: boolean` — whether clicking the mask closes the preview (when `false`, mask clicks should not close the preview)

## Acceptance Criteria

1. TypeScript compilation succeeds with no errors
2. The existing Image component Jest tests pass
3. Biome checks on `components/image` pass
4. ESLint checks on `components/image` pass
