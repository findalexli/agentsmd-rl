# ImageEditor brush preview has a dead zone on vertical images

## Bug

When a user loads a vertical (portrait) image into `gr.ImageEditor`, the real-time brush preview only renders in the top portion of the canvas. The bottom part of the image becomes a "dead zone" where brush strokes still apply (visible on mouse release), but the live preview while drawing is invisible.

This is most pronounced with tall portrait images because the canvas height grows significantly beyond the initial canvas size set during component initialization.

## Reproduction

1. Launch a Gradio app with a `gr.ImageEditor`
2. Load a tall vertical/portrait image
3. Select the brush tool and try drawing in the lower portion of the image
4. Notice the brush preview is not visible in the bottom area, even though strokes appear on mouse release

## Root cause area

The issue is in the brush tool's texture management in:
- `js/imageeditor/shared/brush/brush.ts` — specifically the `set_tool()` method
- `js/imageeditor/shared/brush/brush-textures.ts` — specifically the `reinitialize()` method

When a new image is loaded, the canvas dimensions change. However, `set_tool()` does not detect that the canvas size has changed — it only checks whether the brush mode changed or textures are uninitialized. The brush textures (including the preview sprite) keep their old dimensions from the initial canvas setup, causing the preview to only cover the original area.

Additionally, the `reinitialize()` method compares container dimensions in a way that incorporates the container's scale transform, giving incorrect results when the image has been scaled to fit.

## Expected behavior

The brush preview should be visible across the entire image after loading any image, regardless of aspect ratio or size changes.
