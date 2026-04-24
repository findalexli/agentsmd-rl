# Bug: Fullscreen button on gr.Image throws "onclick is not a function"

## Description

When using `gr.Image` with the `"fullscreen"` button enabled, clicking the fullscreen
button in preview mode throws a JavaScript error:

```
TypeError: onclick is not a function
```

The image displays correctly and the download button works fine, but the fullscreen
toggle is completely broken.

## Reproduction

```python
import gradio as gr

demo = gr.Interface(
    fn=lambda x: x,
    inputs=gr.Image(),
    outputs=gr.Image(buttons=["download", "fullscreen"]),
)
demo.launch()
```

1. Upload any image
2. The output image renders in preview mode with download and fullscreen buttons
3. Click the fullscreen button (maximize icon)
4. **Expected**: Image enters fullscreen mode
5. **Actual**: JavaScript error, nothing happens

## Context

The `FullscreenButton` component (in `js/atoms/src/FullscreenButton.svelte`) expects a
callback prop to handle fullscreen toggling. However, `ImagePreview.svelte`
(`js/image/shared/ImagePreview.svelte`) does not wire up this callback correctly — it
uses an event-based pattern that the `FullscreenButton` component does not support.

A similar issue was previously fixed for the Gallery component. The same pattern needs
to be applied to `ImagePreview`.

## Files of Interest

- `js/image/shared/ImagePreview.svelte` — where the `FullscreenButton` is rendered
- `js/atoms/src/FullscreenButton.svelte` — the button component's expected API

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`
- `eslint (JS/TS linter)`
