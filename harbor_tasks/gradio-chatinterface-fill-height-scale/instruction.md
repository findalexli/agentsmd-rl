# ChatInterface fill_height no longer fills the browser viewport

## Bug Description

`ChatInterface(fill_height=True)` (the default) no longer fills the browser viewport in Gradio 6.x. The chatbot area stays at a fixed ~400px height instead of expanding to fill available space.

This regression was introduced during the Svelte 5 migration. The old initialization code propagated the `fill_height` configuration to the root column by setting `scale` when `fill_height` was true. The new `AppTree` class in `init.svelte.ts` dropped this propagation entirely.

## Expected Behavior

1. When `ChatInterface(fill_height=True)` is created, the internal Chatbot component should use its default height (not a hardcoded 400), allowing CSS flex layout to expand it to fill the viewport.

2. The `fill_height` property from the app configuration must propagate to the frontend and influence the root column's `scale` property. When `fill_height` is true, the root column should have `scale` set to expand and fill available space.

3. The frontend TypeScript `AppConfig` interface must include `fill_height` as a property so the configuration can be properly typed and passed through.

4. The config object passed to `AppTree` and its `reload()` method must include the `fill_height` property.

## Reproduction

```python
import gradio as gr

def echo(message, history):
    return f"Echo: {message}"

demo = gr.ChatInterface(fn=echo, fill_height=True)
demo.launch()
```

The chatbot area should expand to fill the browser viewport, but instead stays at a fixed height.

## Affected Files

- `gradio/chat_interface.py` - Backend ChatInterface component
- `js/core/src/init.svelte.ts` - Frontend AppTree initialization
- `js/core/src/Blocks.svelte` - Frontend config forwarding
- `js/core/src/types.ts` - Frontend TypeScript interfaces
