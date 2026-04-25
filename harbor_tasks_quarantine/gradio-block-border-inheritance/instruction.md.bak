# Bug: Child components inside `gr.HTML` layout lose their borders

## Summary

When `gr.HTML` is used as a layout container (i.e., with children placed inside it), child components unexpectedly lose their borders. This happens because the `Block` Svelte component's approach to hiding borders on container-less blocks inadvertently affects all descendant blocks.

## Reproduction

Create a Gradio app that uses `gr.HTML` as a layout with child components:

```python
import gradio as gr

with gr.Blocks() as demo:
    with gr.HTML():
        tb = gr.Textbox(label="Name")
        btn = gr.Button("Submit")

demo.launch()
```

The `Textbox` and `Button` inside the `gr.HTML` layout will have no visible borders, even though they should.

## Root Cause

The issue is in `js/atoms/src/Block.svelte`. When a block has no explicit container (the `.hide-container` CSS class), the border is currently removed by modifying a CSS custom property. Since CSS custom properties are inherited by child elements, this border removal cascades down to all nested blocks — not just the container-less parent.

## Expected Behavior

Only the container-less block itself should have its border hidden. Child blocks should retain their normal border styling.

## Relevant Files

- `js/atoms/src/Block.svelte` — the `Block` component's template and styles
