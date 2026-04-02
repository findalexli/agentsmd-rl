# ChatInterface fill_height no longer fills the browser viewport

## Bug Description

`ChatInterface(fill_height=True)` (the default) no longer fills the browser viewport in Gradio 6.x. The chatbot area stays at a fixed ~400px height instead of expanding to fill available space.

This regression was introduced during the Svelte 5 migration. The old initialization code (`_init.ts`) propagated the `fill_height` configuration to the root column by setting `scale: 1` when `fill_height` was true. The new `AppTree` class in `init.svelte.ts` dropped this propagation entirely.

## Where to look

There are two sides to this bug:

### Frontend (JavaScript/Svelte)

1. **`js/core/src/init.svelte.ts`** — The `AppTree` class constructs the root column component but does not use the `fill_height` config to influence the root column's layout properties. Compare with the old `_init.ts` logic that was removed during the migration.

2. **`js/core/src/Blocks.svelte`** — The config object passed to the `AppTree` constructor and to the `reload()` method is missing the `fill_height` property. Both call sites need to forward this value from the app config.

3. **`js/core/src/types.ts`** — The `AppConfig` TypeScript interface may need updating to include the `fill_height` property.

### Backend (Python)

4. **`gradio/chat_interface.py`** — In the `_render_chatbot_area` method (~line 332), the default `Chatbot` is created with `height=400 if self.fill_height else None`. This explicit height override conflicts with the fill-height layout behavior. When `fill_height=True`, the chatbot should use its default height and let the CSS flex layout handle expansion.

## Reproduction

```python
import gradio as gr

def echo(message, history):
    return f"Echo: {message}"

demo = gr.ChatInterface(fn=echo, fill_height=True)
demo.launch()
```

The chatbot area should expand to fill the browser viewport, but instead stays at a fixed height.
