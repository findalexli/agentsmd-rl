# Bug: Load event values lost for components in inactive tabs

## Summary

When `demo.load()` targets a component that lives inside an inactive `gr.Tab`, the value set by the load event is silently lost. When the user later clicks on the tab to reveal the component, it appears empty instead of showing the expected value.

## Reproduction

```python
import gradio as gr

with gr.Blocks() as demo:
    with gr.Tab('Tab 1'):
        with gr.Row():
            gr.Chatbot()
            with gr.Column():
                gr.Slider()
                gr.Slider()
                gr.Slider()

    with gr.Tab('Tab 2'):
        textbox = gr.Textbox(label="Output")

    demo.load(
        fn=lambda: 'some text',
        inputs=None,
        outputs=textbox,
    )

if __name__ == "__main__":
    demo.launch()
```

1. Launch the app above
2. Wait for it to load (the `demo.load` event fires on startup)
3. Click "Tab 2"
4. **Expected**: The textbox shows "some text"
5. **Actual**: The textbox is empty

## Root Cause Area

The issue is in `js/core/src/init.svelte.ts`, specifically in how `update_state` and `register_component` interact when a component is hidden in an inactive tab.

When the load event fires, the target component hasn't mounted yet (it's in an inactive tab, so it has no `_set_data` callback). The `update_state` method falls back to updating the node's props directly, but when the component later mounts asynchronously, the Svelte 5 `$effect` syncs from the node's props and overwrites the values.

Additionally, `render_previously_invisible_children` does a full tree traversal and reassignment even when no nodes need to change, which can trigger unnecessary reactive cascades.

## Key Files

- `js/core/src/init.svelte.ts` — The `AppTree` class, specifically `update_state()`, `register_component()`, and `render_previously_invisible_children()`
