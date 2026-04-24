# Add closable Support for Image Preview Mask

## Problem

The Image component's preview mask configuration does not expose a way to control whether clicking the mask closes the preview. When users click on the mask/overlay area of an image preview, it currently always closes the preview. Users need the ability to disable this behavior so that clicking the mask does not close the preview.

## Requirements

1. **Image component**: The `preview.mask` configuration should accept a `closable` boolean option. When `closable: false`, clicking the mask should not close the preview.

2. **Image.PreviewGroup component**: The `preview.mask` configuration should accept a `closable` boolean option with the same behavior as Image.

3. **ConfigProvider**: Should support a global `image.preview.mask.closable` configuration option. Individual component settings should override the global configuration.

## Mask Configuration Schema

The `mask` property in preview options should support:
- `boolean` — enable/disable mask
- `Object` — with the following optional properties:
  - `enabled?: boolean` — whether the mask is enabled
  - `blur?: boolean` — whether to apply blur effect
  - `closable?: boolean` — whether clicking the mask closes the preview

## Acceptance Criteria

1. TypeScript compilation succeeds with no errors
2. The existing Image component Jest tests pass
3. Biome checks on `components/image` pass
4. ESLint checks on `components/image` pass
