# Fix Image Positioning in Crop Editor

## Problem

When dragging an image in the crop editor, the image positioning behaves incorrectly. The crop area moves in the wrong direction relative to the drag gesture, causing a frustrating user experience where the image appears to "jump" or move opposite to where the user is dragging.

## Affected Code

The bug is in the drag handling logic in the crop editor. Look at `packages/excalidraw/components/App.tsx` in the pointer move handling code (around line 9020 and the crop editor section around line 9388).

## What Needs to Be Fixed

1. **Track previous pointer coordinates**: The current code tracks `lastPointerMoveCoords` for the current frame, but the drag calculation needs the **previous frame's** pointer coordinates to correctly compute the offset.

2. **Fix the crop offset calculation**: When calculating the new crop position, the sign of the offset vector is incorrect. The crop position should subtract the offset (not add it) to move in the correct direction relative to the drag gesture.

3. **Reset state properly**: The previous pointer coordinate tracking should be reset when the drag ends (on pointer up).

## Expected Behavior

After the fix, when a user drags the image in the crop editor:
- The image should move in the same direction as the drag gesture
- The movement should be smooth without jumps
- The crop coordinates should correctly follow the pointer movement

## Hints

- Look for where `lastPointerMoveCoords` is used in drag calculations
- Find the crop editor section where `offsetVector` is applied to `crop.x` and `crop.y`
- The fix involves introducing a new field to track previous frame coordinates
- Both the x and y crop coordinate calculations have the same sign error
