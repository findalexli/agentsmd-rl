# Fix Crop Editor Cursor Drift

## Problem

In the image crop editor, when dragging to crop an image that is displayed at a different scale than its natural size (e.g., a 2x-scaled image), the cursor movement drifts — the image appears to move ahead of or behind the actual cursor position.

## Expected Behavior

When dragging to crop, the image under the cursor should follow the mouse pointer precisely, regardless of the image's display scale on the canvas.

## Context

The drag offset calculation in the cropping logic uses a zoom-based scaling factor that doesn't account for the ratio between the image's natural dimensions and its current displayed dimensions on the canvas. This causes the visual feedback to diverge from the cursor position when the image is scaled.

The code that computes drag offset currently applies a scaling factor of `Math.max(this.state.zoom.value, 2)` via a `vectorScale` call. This zoom-based value is incorrect — the correct approach uses the image's `naturalWidth` and `naturalHeight` properties scaled by the uncropped dimensions obtained from `getUncroppedWidthAndHeight`.

## What to Fix

Find and fix the drag offset calculation in the cropping code path in `packages/excalidraw/components/App.tsx`. The current implementation uses `Math.max(this.state.zoom.value, 2)` with `vectorScale`. Replace this with a calculation that uses `naturalWidth` and `naturalHeight` (from the image element) and obtains uncropped dimensions via `getUncroppedWidthAndHeight` from `@excalidraw/element`.

## Verification

After the fix:
- `npx tsc --noEmit` should pass with no errors
- `yarn eslint --max-warnings=0 packages/excalidraw/components/App.tsx` should pass
- `yarn vitest run packages/element/tests/cropElement.test.tsx` should pass
- `yarn vitest run packages/excalidraw/tests/image.test.tsx` should pass
- `yarn vitest run packages/element/tests/` should pass

Cropping an image at any display scale should result in the image precisely following the cursor with no drift.