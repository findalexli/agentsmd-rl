# Bug: Child components inside `gr.HTML` layout lose their borders

## Summary

When `gr.HTML` is used as a layout container (i.e., with children placed inside it), child components unexpectedly lose their borders. This happens because the border-hiding mechanism for container-less blocks inadvertently cascades to all descendant blocks.

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

The `Textbox` and `Button` inside the `gr.HTML` layout will have no visible borders, even though they should retain their normal border styling.

## Expected Behavior

- Container-less layout blocks (like those used internally by `gr.HTML`) should hide their own borders
- Child blocks nested inside these containers should retain their normal border styling
- Only the container-less block itself should have its border hidden; children should not be affected

## Required Verification

After the fix, the following must hold in `js/atoms/src/Block.svelte`:

1. The `.hide-container:not(.fullscreen)` CSS class must set its own border directly to zero, without using the `--block-border-width` CSS variable
2. The `.hide-container:not(.fullscreen)` CSS class must NOT set `--block-border-width: 0` (this is the root cause - it inherits to children)
3. The `.block` CSS class must set `border-width: var(--block-border-width)` to ensure it always uses its own border width
4. The `.hide-container:not(.fullscreen)` CSS class must preserve its other CSS resets: `margin: 0`, `box-shadow: none`, `background: transparent`, `padding: 0`, `overflow: visible`
5. The template must NOT apply `border-width` via inline style attribute on the block element (this overrides the CSS class-based border)
6. The template must still contain: `class:hide-container`, `class:fullscreen`, `style:flex-grow`, and `<slot`
7. The `.block` CSS class must retain: `box-shadow:`, `border-color:`, `border-radius:`, and `background:`
