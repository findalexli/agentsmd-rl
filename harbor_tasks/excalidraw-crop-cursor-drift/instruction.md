# Fix Crop Editor Cursor Drift

## Problem

In the image crop editor, when dragging to crop an image with non-1x scaling, the cursor movement drifts either ahead of or behind the actual image being dragged. This causes a poor user experience where the visual feedback doesn't match the cursor position.

## Location

The issue is in the cropping/dragging logic in:
- `packages/excalidraw/components/App.tsx`

Look for the code that handles drag offset calculation during image cropping operations. The relevant code involves:
- Pointer coordinate tracking during drag operations
- Image scaling calculations
- The `vectorScale` function and zoom-based scaling

## What Needs to Change

The drag offset calculation needs to account for the actual canvas image element scaling using the image's natural dimensions, rather than relying solely on zoom level. The fix should:

1. Use the image's natural dimensions (naturalWidth/naturalHeight) relative to the uncropped element size
2. Apply the correct scaling ratio to the drag offset vector
3. Remove any zoom-based scaling that doesn't account for the actual image-to-canvas scaling ratio

## Expected Behavior

After the fix, when cropping an image at any zoom level, the image should follow the cursor precisely without drifting ahead or behind the mouse pointer.

## Hints

- Look at how `vectorScale` is currently being used in the cropping logic
- The element has information about its cropped and uncropped dimensions
- The fix involves comparing the image's natural size to the displayed element size
- You may need to import a helper function from `@excalidraw/element` to get uncropped dimensions
